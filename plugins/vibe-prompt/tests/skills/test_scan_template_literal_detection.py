r"""
Task 6 — TDD tests for template-literal interpolation detection in scan/SKILL.md.

Pattern: `\`...${varName}...\``
Capture: name, source: 'template-literal', declaredAt (file:line).

Asserts:
  1. scan/SKILL.md references template-literal detection in its workflow
  2. references/inline-prompt-detection.md exists and declares the pattern
  3. The detection rule includes the ${...} syntax marker
  4. The captured shape declares name + source: 'template-literal' + declaredAt
  5. The reference file ties into the inventory schema's templatedVar shape (object form)
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
SCAN_SKILL = SKILLS_DIR / "scan" / "SKILL.md"
INLINE_PROMPT_REF = SKILLS_DIR / "scan" / "references" / "inline-prompt-detection.md"


class TestScanTemplateLiteralDetection(unittest.TestCase):

    def setUp(self):
        self.skill = SCAN_SKILL.read_text(encoding="utf-8") if SCAN_SKILL.exists() else ""
        self.ref = (
            INLINE_PROMPT_REF.read_text(encoding="utf-8")
            if INLINE_PROMPT_REF.exists()
            else ""
        )
        self.combined = self.skill + "\n" + self.ref

    def test_inline_prompt_detection_reference_exists(self):
        self.assertTrue(
            INLINE_PROMPT_REF.exists(),
            "scan/references/inline-prompt-detection.md must exist",
        )

    def test_skill_references_inline_prompt_detection(self):
        self.assertIn(
            "inline-prompt-detection",
            self.skill,
            "scan/SKILL.md must reference inline-prompt-detection.md",
        )

    def test_template_literal_pattern_documented(self):
        """Reference must declare the `${var}` template-literal pattern."""
        has_pattern = (
            "${" in self.combined
            and "template-literal" in self.combined
        )
        self.assertTrue(
            has_pattern,
            "template-literal pattern with ${...} interpolation must be documented",
        )

    def test_template_literal_source_value_declared(self):
        self.assertIn(
            "template-literal",
            self.ref,
            "inline-prompt-detection.md must declare source value 'template-literal'",
        )

    def test_captured_shape_includes_name_and_declaredAt(self):
        has_name = "name" in self.ref.lower()
        has_declared_at = "declaredAt" in self.ref or "declared at" in self.ref.lower()
        self.assertTrue(
            has_name and has_declared_at,
            "Captured var shape must include name + declaredAt",
        )

    def test_emits_object_form_for_template_literal(self):
        """When template-literal pattern is captured, output must be the object form."""
        # The reference must explicitly note object-shape emission for new patterns
        self.assertTrue(
            "object" in self.ref.lower(),
            "inline-prompt-detection.md must note object-form emission for non-handlebars patterns",
        )


if __name__ == "__main__":
    unittest.main()
