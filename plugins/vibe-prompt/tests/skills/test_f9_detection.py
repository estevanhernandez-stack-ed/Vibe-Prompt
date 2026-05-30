"""
Task 7 — TDD tests for F9 detection in audit/SKILL.md.

SKILL.md is a prose workflow document, not executable code. These tests validate
that the SKILL contains the necessary detection rule prose so the agent following
the SKILL can correctly perform F9 detection.

Asserts:
  1. audit/SKILL.md references smell-rubric-f1-f13.md (cross-ref update done in Task 6)
  2. SKILL contains F9 detection step in the workflow
  3. SKILL includes the date-keyword regex pattern (or references the rubric for it)
  4. SKILL includes the composition-stack temporal anchor check logic
  5. SKILL includes false-positive escape hatch (--ignore-finding F9)
  6. SKILL includes composer-mimic confidence degrade (< 0.6 → medium severity)
  7. SKILL includes the apply-rubric step that walks F9
"""

import pathlib
import unittest

SKILLS_DIR = (
    pathlib.Path(__file__).parent.parent.parent
    / "skills"
)
AUDIT_SKILL = SKILLS_DIR / "audit" / "SKILL.md"
AUDIT_RUBRIC = SKILLS_DIR / "audit" / "references" / "smell-rubric-f1-f13.md"


class TestF9DetectionInAuditSkill(unittest.TestCase):

    def setUp(self):
        self.skill_content = AUDIT_SKILL.read_text(encoding="utf-8")
        self.rubric_content = AUDIT_RUBRIC.read_text(encoding="utf-8")

    # ------------------------------------------------------------------ #
    # 1. SKILL references the renamed rubric                              #
    # ------------------------------------------------------------------ #

    def test_skill_references_f1_f12_rubric(self):
        self.assertIn(
            "smell-rubric-f1-f13.md",
            self.skill_content,
            "audit/SKILL.md must reference smell-rubric-f1-f13.md (not the old f1-f7)"
        )

    def test_skill_does_not_reference_old_rubric(self):
        self.assertNotIn(
            "smell-rubric-f1-f7.md",
            self.skill_content,
            "audit/SKILL.md still has stale reference to smell-rubric-f1-f7.md"
        )

    # ------------------------------------------------------------------ #
    # 2. F9 step is present in the Apply-rubric workflow                  #
    # ------------------------------------------------------------------ #

    def test_skill_workflow_walks_f9(self):
        self.assertIn(
            "F9",
            self.skill_content,
            "audit/SKILL.md workflow step must include F9"
        )

    # ------------------------------------------------------------------ #
    # 3. Date-keyword detection — either inline or via rubric reference   #
    # ------------------------------------------------------------------ #

    def test_f9_date_keyword_detection_referenced(self):
        """The SKILL or rubric must document date-keyword regex detection."""
        combined = self.skill_content + self.rubric_content
        # Either the SKILL names the regex inline or the rubric covers it
        has_keyword_ref = (
            "birth" in combined.lower()
            and ("natal" in combined.lower() or "today" in combined.lower())
            and ("keyword" in combined.lower() or "regex" in combined.lower())
        )
        self.assertTrue(
            has_keyword_ref,
            "F9 detection must reference date-keyword / regex pattern (birth, natal, today, etc.)"
        )

    # ------------------------------------------------------------------ #
    # 4. Composition-stack temporal anchor check                          #
    # ------------------------------------------------------------------ #

    def test_f9_composition_stack_check_referenced(self):
        """SKILL or rubric must mention composition-stack anchor check for F9."""
        combined = self.skill_content + self.rubric_content
        self.assertTrue(
            "composition stack" in combined.lower()
            or "temporal anchor" in combined.lower()
            or "[current date]" in combined.lower(),
            "F9 must document the composition-stack temporal anchor check"
        )

    # ------------------------------------------------------------------ #
    # 5. False-positive escape hatch                                      #
    # ------------------------------------------------------------------ #

    def test_f9_false_positive_escape_hatch_referenced(self):
        """SKILL or rubric must mention the --ignore-finding F9 escape."""
        combined = self.skill_content + self.rubric_content
        self.assertTrue(
            "--ignore-finding" in combined or "ignore-finding" in combined,
            "F9 must document the --ignore-finding F9 --on-prompt <id> escape hatch"
        )

    # ------------------------------------------------------------------ #
    # 6. Composer-mimic confidence degrade                                #
    # ------------------------------------------------------------------ #

    def test_f9_confidence_degrade_referenced(self):
        """SKILL or rubric must mention the confidence < 0.6 → medium severity rule."""
        combined = self.skill_content + self.rubric_content
        self.assertTrue(
            "0.6" in combined or "confidence" in combined.lower(),
            "F9 must document the composer-mimic confidence < 0.6 → medium severity rule"
        )

    # ------------------------------------------------------------------ #
    # 7. Rubric recommendation template matches spec                      #
    # ------------------------------------------------------------------ #

    def test_f9_recommendation_template_present(self):
        """Rubric must contain a recommendation template for F9."""
        self.assertIn(
            "composition stack has no current-date anchor",
            self.rubric_content,
            "F9 recommendation template (or equivalent) missing from rubric"
        )

    def test_f9_evidence_promptId_referenced(self):
        """F9 evidence shape must include promptId."""
        self.assertIn(
            "promptId",
            self.rubric_content,
            "F9 evidence shape must reference promptId"
        )

    def test_f9_evidence_dateKeywords_referenced(self):
        """F9 evidence shape must include dateKeywords."""
        self.assertIn(
            "dateKeywords",
            self.rubric_content,
            "F9 evidence shape must reference dateKeywords"
        )


if __name__ == "__main__":
    unittest.main()
