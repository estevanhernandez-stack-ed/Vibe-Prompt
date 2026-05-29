r"""
Task 8 — TDD tests for JSX-attr inline prompt detection in scan/SKILL.md.

Pattern: `<Component prompt={`...${var}...`} userPrompt={`...${var}...`}>`
Capture: name, source: 'jsx-attr', declaredAt.

Asserts:
  1. inline-prompt-detection.md declares the jsx-attr pattern
  2. source value 'jsx-attr' is documented
  3. The reference shows a JSX attribute example with a template literal value
  4. Detection is scoped to .tsx/.jsx files only
  5. Detection runs per attribute (multiple attrs on same component → multiple captures)
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
SCAN_SKILL = SKILLS_DIR / "scan" / "SKILL.md"
INLINE_PROMPT_REF = SKILLS_DIR / "scan" / "references" / "inline-prompt-detection.md"


class TestScanJsxAttrDetection(unittest.TestCase):

    def setUp(self):
        self.skill = SCAN_SKILL.read_text(encoding="utf-8")
        self.ref = INLINE_PROMPT_REF.read_text(encoding="utf-8")

    def test_jsx_attr_source_value_declared(self):
        self.assertIn(
            "jsx-attr",
            self.ref,
            "inline-prompt-detection.md must declare source value 'jsx-attr'",
        )

    def test_jsx_attr_example_shows_template_literal_value(self):
        """Example must show JSX attr with `{`...${var}...`}` value."""
        has_jsx = (
            ("<" in self.ref and "/>" in self.ref)
            or "Component" in self.ref
            or "tsx" in self.ref.lower()
        )
        self.assertTrue(
            has_jsx,
            "inline-prompt-detection.md must show a JSX-attr example",
        )

    def test_jsx_attr_file_scope_documented(self):
        """Detection must specify .tsx/.jsx scope."""
        has_scope = (
            ".tsx" in self.ref
            and ".jsx" in self.ref
        )
        self.assertTrue(
            has_scope,
            "JSX-attr detection must document .tsx/.jsx file scope",
        )

    def test_jsx_attr_per_attribute_capture(self):
        """Multiple JSX attrs on the same component → multiple captures."""
        ref_lower = self.ref.lower()
        has_multiple = (
            "each attribute" in ref_lower
            or "per attribute" in ref_lower
            or "independently" in ref_lower
            or "systempr" in ref_lower  # multi-attr example uses systemPrompt+userPrompt
        )
        self.assertTrue(
            has_multiple,
            "JSX-attr detection must document per-attribute capture (multi-attr → multi-capture)",
        )

    def test_skill_workflow_mentions_jsx_attr_pattern(self):
        """SKILL.md workflow must mention jsx-attr as one of the patterns."""
        self.assertIn(
            "jsx-attr",
            self.skill,
            "scan/SKILL.md workflow must reference jsx-attr detection",
        )


if __name__ == "__main__":
    unittest.main()
