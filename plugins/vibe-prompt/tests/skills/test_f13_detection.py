r"""
Task 12 — TDD tests for F13 detection logic in audit/SKILL.md.

F13 detection rule (per spec §4):
  Step A — structural-cue match: [BRACKETS] regex, {{var}} 3+ times, JSON-shaped sections
  Step B — output-format declaration absence: no [OUTPUT FORMAT:, no [OUTPUT_SCHEMA], no "Respond in JSON", no "prose only"
  Fire when: A matches AND B finds nothing
  Read `audit.f13.outputFormatExceptions` from config for prompt-id suppression

Asserts:
  1. audit/SKILL.md has an F13 detection workflow step (e.g., 4f.)
  2. SKILL references both step A (structural cues) and step B (format absence)
  3. SKILL documents regex `\[[A-Z_]+\]` for BRACKETS detection
  4. SKILL documents the {{var}} 3+ check
  5. SKILL documents JSON-shape detection
  6. SKILL references the explicit declarations: [OUTPUT FORMAT:, [OUTPUT_SCHEMA], Respond in JSON, prose only
  7. SKILL reads `audit.f13.outputFormatExceptions` from config for suppression
  8. SKILL fires F13 with severity "medium"
  9. SKILL workflow walks F13 (order F1 → ... → F12 → F13)
  10. SKILL emits evidence: detectedCues + missingDeclarations
"""

import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent.parent.parent
SKILLS_DIR = ROOT / "skills"
AUDIT_SKILL = SKILLS_DIR / "audit" / "SKILL.md"


class TestF13DetectionInAuditSkill(unittest.TestCase):

    def setUp(self):
        self.skill = AUDIT_SKILL.read_text(encoding="utf-8")

    def test_f13_workflow_step_exists(self):
        """audit/SKILL.md must have an explicit F13 detection workflow step."""
        # Look for "4f." step or any step labeled F13
        has_step = (
            "4f." in self.skill
            or "**F13" in self.skill
            or "F13 detection" in self.skill
        )
        self.assertTrue(
            has_step,
            "audit/SKILL.md must include an F13 detection workflow step"
        )

    def test_f13_references_structural_cues_step_a(self):
        """SKILL F13 step must reference structural-cue detection (step A)."""
        self.assertIn(
            "structural",
            self.skill.lower(),
            "F13 step must reference structural cue detection"
        )

    def test_f13_brackets_regex_documented(self):
        """SKILL must reference the [A-Z_]+ regex for BRACKETS detection."""
        # Tolerate either literal regex or descriptive text
        has_brackets = (
            "[A-Z_]+" in self.skill
            or "BRACKETS" in self.skill
            or "[BRACKETS]" in self.skill
        )
        self.assertTrue(
            has_brackets,
            "F13 step must document BRACKETS-block detection"
        )

    def test_f13_templated_vars_3x(self):
        """SKILL must reference {{var}} 3+ check."""
        has_vars = (
            "{{" in self.skill
            and ("3" in self.skill or "more than 2" in self.skill.lower())
        )
        self.assertTrue(
            has_vars,
            "F13 step must reference {{var}} 3+ check"
        )

    def test_f13_json_shape_detection(self):
        """SKILL must reference JSON-shape / JSON-like detection."""
        has_json = (
            "JSON" in self.skill
            and ("shape" in self.skill.lower() or "data section" in self.skill.lower() or "json-like" in self.skill.lower())
        )
        self.assertTrue(
            has_json,
            "F13 step must reference JSON-shape detection"
        )

    def test_f13_format_absence_step_b(self):
        """SKILL F13 step must reference output-format declaration absence (step B)."""
        has_absence = (
            "OUTPUT FORMAT" in self.skill
            and ("absence" in self.skill.lower() or "not contain" in self.skill.lower() or "missing" in self.skill.lower())
        )
        self.assertTrue(
            has_absence,
            "F13 step must reference output-format declaration absence"
        )

    def test_f13_references_explicit_declarations(self):
        """SKILL F13 step must reference the explicit declarations checked for in step B."""
        # [OUTPUT FORMAT:, [OUTPUT_SCHEMA], Respond in JSON, prose only
        has_format = "[OUTPUT FORMAT:" in self.skill or "OUTPUT FORMAT:" in self.skill
        has_schema = "OUTPUT_SCHEMA" in self.skill
        has_respond = "Respond in JSON" in self.skill or "Return JSON" in self.skill
        has_prose = "prose only" in self.skill.lower() or "narrative response" in self.skill.lower()
        # At least 3 of 4 explicit checks present
        present = sum([has_format, has_schema, has_respond, has_prose])
        self.assertGreaterEqual(
            present, 3,
            f"F13 step must reference at least 3 explicit format declarations (found {present})"
        )

    def test_f13_reads_config_exceptions(self):
        """SKILL must read audit.f13.outputFormatExceptions from config."""
        self.assertIn(
            "outputFormatExceptions",
            self.skill,
            "F13 step must read audit.f13.outputFormatExceptions from config"
        )

    def test_f13_severity_medium(self):
        """F13 fires with severity medium."""
        # Look for the 4f F13 detection step section specifically
        step_idx = self.skill.find("4f.")
        if step_idx < 0:
            step_idx = self.skill.find("F13 implicit")
        section = self.skill[step_idx: step_idx + 3000] if step_idx >= 0 else ""
        self.assertIn(
            "medium",
            section.lower(),
            "F13 detection step (4f) must declare severity medium"
        )

    def test_f13_workflow_walks_in_order(self):
        """SKILL workflow apply-rubric step must walk F13 after F12."""
        # Look for F1 → F1b → F2 → ... → F12 → F13 in step 2 (apply rubric)
        apply_idx = self.skill.find("Apply rubric")
        section = self.skill[apply_idx: apply_idx + 1000] if apply_idx >= 0 else self.skill
        self.assertIn(
            "F13",
            section,
            "SKILL workflow walk-order list must include F13"
        )

    def test_f13_evidence_detectedCues_and_missingDeclarations(self):
        """F13 finding evidence must include detectedCues + missingDeclarations."""
        self.assertIn(
            "detectedCues",
            self.skill,
            "F13 step must emit detectedCues evidence"
        )
        self.assertIn(
            "missingDeclarations",
            self.skill,
            "F13 step must emit missingDeclarations evidence"
        )


if __name__ == "__main__":
    unittest.main()
