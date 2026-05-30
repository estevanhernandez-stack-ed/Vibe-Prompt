"""
Task 11 — TDD tests for renaming smell-rubric-f1-f12.md → smell-rubric-f1-f13.md
and adding F13 section.

Asserts:
  1. smell-rubric-f1-f13.md exists
  2. smell-rubric-f1-f12.md does NOT exist (renamed away)
  3. The renamed file contains the F13 section heading
  4. F13 section declares severity = medium
  5. F13 documents detection rule (structural cues + missing format declaration)
  6. F13 documents evidence shape (detectedCues, missingDeclarations)
  7. F13 documents score impact reference
  8. No SKILL files still reference the old `smell-rubric-f1-f12.md` path
"""

import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent.parent.parent
SKILLS_DIR = ROOT / "skills"
OLD_RUBRIC = SKILLS_DIR / "audit" / "references" / "smell-rubric-f1-f12.md"
NEW_RUBRIC = SKILLS_DIR / "audit" / "references" / "smell-rubric-f1-f13.md"


class TestSmellRubricF1F13(unittest.TestCase):

    def test_new_rubric_file_exists(self):
        self.assertTrue(
            NEW_RUBRIC.exists(),
            f"smell-rubric-f1-f13.md must exist at {NEW_RUBRIC}"
        )

    def test_old_rubric_file_removed(self):
        self.assertFalse(
            OLD_RUBRIC.exists(),
            f"smell-rubric-f1-f12.md must be renamed away (not exist at {OLD_RUBRIC})"
        )

    def test_f13_section_present(self):
        content = NEW_RUBRIC.read_text(encoding="utf-8") if NEW_RUBRIC.exists() else ""
        self.assertIn(
            "## F13",
            content,
            "smell-rubric-f1-f13.md must contain ## F13 section heading"
        )

    def test_f13_section_severity_medium(self):
        content = NEW_RUBRIC.read_text(encoding="utf-8") if NEW_RUBRIC.exists() else ""
        f13_start = content.find("## F13")
        f13_section = content[f13_start: f13_start + 5000] if f13_start >= 0 else ""
        self.assertIn(
            "medium",
            f13_section.lower(),
            "F13 must declare severity medium"
        )

    def test_f13_section_detection_rule_cues_and_format_absence(self):
        content = NEW_RUBRIC.read_text(encoding="utf-8") if NEW_RUBRIC.exists() else ""
        f13_start = content.find("## F13")
        f13_section = content[f13_start: f13_start + 5000] if f13_start >= 0 else ""
        # Structural cues: brackets / templated vars / json-shape
        has_cue = (
            "BRACKETS" in f13_section
            or "structural cue" in f13_section.lower()
            or "{{" in f13_section
        )
        # Output format absence
        has_absence = (
            "OUTPUT FORMAT" in f13_section
            or "output format" in f13_section.lower()
        )
        self.assertTrue(
            has_cue and has_absence,
            "F13 detection rule must reference structural cues AND output-format absence"
        )

    def test_f13_evidence_includes_detectedCues(self):
        content = NEW_RUBRIC.read_text(encoding="utf-8") if NEW_RUBRIC.exists() else ""
        f13_start = content.find("## F13")
        f13_section = content[f13_start: f13_start + 5000] if f13_start >= 0 else ""
        self.assertIn(
            "detectedCues",
            f13_section,
            "F13 evidence must include detectedCues field"
        )

    def test_f13_evidence_includes_missingDeclarations(self):
        content = NEW_RUBRIC.read_text(encoding="utf-8") if NEW_RUBRIC.exists() else ""
        f13_start = content.find("## F13")
        f13_section = content[f13_start: f13_start + 5000] if f13_start >= 0 else ""
        self.assertIn(
            "missingDeclarations",
            f13_section,
            "F13 evidence must include missingDeclarations field"
        )

    def test_f13_documents_score_impact(self):
        content = NEW_RUBRIC.read_text(encoding="utf-8") if NEW_RUBRIC.exists() else ""
        f13_start = content.find("## F13")
        f13_section = content[f13_start: f13_start + 5000] if f13_start >= 0 else ""
        # schema-tightness −2 and instruction-clarity −1
        has_schema = "schema" in f13_section.lower() and ("−2" in f13_section or "-2" in f13_section)
        has_clarity = "clarity" in f13_section.lower() and ("−1" in f13_section or "-1" in f13_section)
        self.assertTrue(
            has_schema and has_clarity,
            "F13 must document score impact: schema-tightness −2, instruction-clarity −1"
        )

    def test_no_skill_references_old_rubric_path(self):
        """No SKILL.md files should still reference smell-rubric-f1-f12.md as a path."""
        for skill_md in SKILLS_DIR.rglob("SKILL.md"):
            content = skill_md.read_text(encoding="utf-8")
            self.assertNotIn(
                "smell-rubric-f1-f12.md",
                content,
                f"{skill_md} still references old smell-rubric-f1-f12.md path"
            )


if __name__ == "__main__":
    unittest.main()
