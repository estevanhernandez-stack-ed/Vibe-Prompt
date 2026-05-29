r"""
Task 9 — TDD tests for unified declaredAt + source tracking integration.

Verifies:
  1. Multi-pattern prompts (handlebars + template-literal + concat in same source)
     produce coherent output per inline-prompt-detection.md
  2. Handlebars-only prompts stay as v0.4 string-array shape
  3. Mixed prompts emit object form for new patterns, string form for handlebars
  4. Output validates against the v0.5 inventory schema (Task 1)
  5. Documentation declares the backward-compat invariant
"""

import json
import pathlib
import unittest

from jsonschema import validate

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
SCHEMAS_DIR = pathlib.Path(__file__).parent.parent.parent / "schemas"
INLINE_PROMPT_REF = SKILLS_DIR / "scan" / "references" / "inline-prompt-detection.md"
INVENTORY_SCHEMA = SCHEMAS_DIR / "inventory.schema.json"


def _make_inventory(inline_vars_list):
    return {
        "version": "0.1",
        "scannedAt": "2026-05-30T09:00:00Z",
        "targetApp": {"name": "test", "stack": ["typescript"], "aiProviders": ["gemini"]},
        "registry": {"detected": False, "entries": []},
        "inlinePrompts": [
            {
                "file": "src/test.tsx",
                "startLine": 1,
                "endLine": 10,
                "outputShape": "prose",
                "templatedVars": inline_vars_list,
                "voiceBearing": True,
            }
        ],
        "personas": [],
        "modelIdentifiers": [],
    }


class TestUnifiedVarTrackingDocumentation(unittest.TestCase):

    def setUp(self):
        self.ref = INLINE_PROMPT_REF.read_text(encoding="utf-8")

    def test_backward_compat_invariant_documented(self):
        """Handlebars-only → string array shape. Documented."""
        ref_lower = self.ref.lower()
        has_invariant = (
            "backward" in ref_lower
            and "v0.4" in self.ref
            and "string" in ref_lower
        )
        self.assertTrue(
            has_invariant,
            "inline-prompt-detection.md must document v0.4 backward-compat (handlebars-only → string)",
        )

    def test_mixed_pattern_output_documented(self):
        """Mixed prompts → handlebars stays string, new patterns emit object."""
        ref_lower = self.ref.lower()
        has_mixed = "mixed" in ref_lower
        self.assertTrue(
            has_mixed,
            "inline-prompt-detection.md must document mixed-pattern output behavior",
        )

    def test_all_four_sources_enumerated(self):
        for src in ("handlebars", "template-literal", "concat", "jsx-attr"):
            self.assertIn(
                src,
                self.ref,
                f"inline-prompt-detection.md must enumerate source value '{src}'",
            )

    def test_detection_order_documented(self):
        """Detection order is explicit (Pattern 1 → 2 → 3 → 4 then dedupe)."""
        ref_lower = self.ref.lower()
        has_order = (
            "detection order" in ref_lower
            or "dedupe" in ref_lower
        )
        self.assertTrue(
            has_order,
            "inline-prompt-detection.md must document detection order + dedupe",
        )


class TestUnifiedOutputValidatesAgainstSchema(unittest.TestCase):
    """Round-trip: outputs in the documented shape validate against inventory.schema.json."""

    def setUp(self):
        with open(INVENTORY_SCHEMA) as f:
            self.schema = json.load(f)

    def test_handlebars_only_validates_as_string_array(self):
        doc = _make_inventory(["{{name}}", "{{date}}"])
        validate(instance=doc, schema=self.schema)

    def test_template_literal_only_validates_as_object_array(self):
        doc = _make_inventory(
            [
                {
                    "name": "dreamText",
                    "source": "template-literal",
                    "declaredAt": "src/test.tsx:L5",
                }
            ]
        )
        validate(instance=doc, schema=self.schema)

    def test_mixed_pattern_validates(self):
        """Mixed: handlebars as string, new patterns as object — both allowed by schema."""
        doc = _make_inventory(
            [
                "{{name}}",
                {
                    "name": "dreamText",
                    "source": "template-literal",
                    "declaredAt": "src/test.tsx:L7",
                },
                {
                    "name": "userMessage",
                    "source": "concat",
                    "declaredAt": "src/test.tsx:L8",
                },
            ]
        )
        validate(instance=doc, schema=self.schema)

    def test_all_object_form_validates(self):
        """Even handlebars-as-object form is allowed."""
        doc = _make_inventory(
            [
                {
                    "name": "name",
                    "source": "handlebars",
                    "declaredAt": "src/test.tsx:L1",
                },
                {
                    "name": "persona",
                    "source": "jsx-attr",
                    "declaredAt": "src/test.tsx:L4",
                },
            ]
        )
        validate(instance=doc, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
