"""
Task 5 (v0.7) — TDD tests for pending-fix.schema.json v0.7 extensions.

Asserts:
  1. findingCategory enum gains D-1, D-2, D-3
  2. migrationKind optional enum
     (D-1-inline-to-registry | D-2-typed-renderer | D-3-model-consolidation)
  3. consolidatedFindingIds optional array of strings
  4. Backward compat: v0.6 pending-fix front-matter validates
"""

import json
import pathlib
import unittest

from jsonschema import validate, ValidationError

SCHEMAS_DIR = pathlib.Path(__file__).parent.parent.parent / "schemas"
SCHEMA_PATH = SCHEMAS_DIR / "pending-fix.schema.json"


def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def _minimal_pending(extras=None):
    doc = {
        "findingId": "F1-1",
        "findingCategory": "A",
        "confidence": 0.8,
        "targetFile": "src/x.ts",
        "targetRange": "10-20",
        "recommendationSource": "category-A-template",
    }
    if extras:
        doc.update(extras)
    return doc


class TestPendingV07CategoryD(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_findingCategory_enum_includes_D1(self):
        self.assertIn(
            "D-1", self.schema["properties"]["findingCategory"]["enum"]
        )

    def test_findingCategory_enum_includes_D2(self):
        self.assertIn(
            "D-2", self.schema["properties"]["findingCategory"]["enum"]
        )

    def test_findingCategory_enum_includes_D3(self):
        self.assertIn(
            "D-3", self.schema["properties"]["findingCategory"]["enum"]
        )

    def test_existing_categories_preserved(self):
        enum_vals = self.schema["properties"]["findingCategory"]["enum"]
        for expected in ["A", "B", "C", "B-voice-frame"]:
            self.assertIn(expected, enum_vals)

    def test_pending_with_D1_category_validates(self):
        doc = _minimal_pending(extras={"findingCategory": "D-1"})
        validate(instance=doc, schema=self.schema)

    def test_pending_with_D3_category_validates(self):
        doc = _minimal_pending(extras={"findingCategory": "D-3"})
        validate(instance=doc, schema=self.schema)


class TestPendingV07MigrationKind(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_migrationKind_field_declared(self):
        self.assertIn("migrationKind", self.schema["properties"])

    def test_migrationKind_enum(self):
        enum_vals = self.schema["properties"]["migrationKind"]["enum"]
        for expected in [
            "D-1-inline-to-registry",
            "D-2-typed-renderer",
            "D-3-model-consolidation",
        ]:
            self.assertIn(expected, enum_vals)

    def test_migrationKind_is_optional(self):
        required = self.schema.get("required", [])
        self.assertNotIn("migrationKind", required)

    def test_pending_with_migrationKind_validates(self):
        doc = _minimal_pending(
            extras={
                "findingCategory": "D-2",
                "migrationKind": "D-2-typed-renderer",
            }
        )
        validate(instance=doc, schema=self.schema)


class TestPendingV07ConsolidatedFindingIds(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_consolidatedFindingIds_field_declared(self):
        self.assertIn("consolidatedFindingIds", self.schema["properties"])

    def test_consolidatedFindingIds_is_string_array(self):
        cfi = self.schema["properties"]["consolidatedFindingIds"]
        self.assertEqual(cfi["type"], "array")
        self.assertEqual(cfi["items"]["type"], "string")

    def test_consolidatedFindingIds_is_optional(self):
        required = self.schema.get("required", [])
        self.assertNotIn("consolidatedFindingIds", required)

    def test_pending_with_consolidated_finding_ids_validates(self):
        doc = _minimal_pending(
            extras={
                "findingCategory": "C",
                "consolidatedFindingIds": ["F11-1", "F12-1"],
            }
        )
        validate(instance=doc, schema=self.schema)


class TestPendingV07BackwardCompat(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_v06_pending_fix_validates(self):
        doc = {
            "findingId": "F4-1",
            "findingCategory": "B-voice-frame",
            "confidence": 0.78,
            "targetFile": "src/prompts/registry.ts",
            "targetRange": "120-150",
            "recommendationSource": "category-B-voice-frame-template",
            "voiceFrameRewriteRationale": "Rewrite aligns with extracted Pilgrim voice rule.",
            "stagedAt": "2026-05-29T18:00:00Z",
        }
        validate(instance=doc, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
