"""
Task 4 (v0.7) — TDD tests for remediate-result.schema.json v0.7 extensions.

Asserts:
  1. appliedDiffs[].migrationKind optional enum
     (D-1-inline-to-registry | D-2-typed-renderer | D-3-model-consolidation)
  2. Top-level consolidatedDiffs[] optional array (each:
     {path, findingIds[], rationale})
  3. Backward compat: v0.6 remediate-result.json validates
"""

import json
import pathlib
import unittest

from jsonschema import validate, ValidationError

SCHEMAS_DIR = pathlib.Path(__file__).parent.parent.parent / "schemas"
SCHEMA_PATH = SCHEMAS_DIR / "remediate-result.schema.json"


def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def _minimal_remediate_result(extra=None):
    doc = {
        "runId": "r-1",
        "timestamp": "2026-06-01T00:00:00Z",
        "auditRunId": "a-1",
        "totalFindings": 0,
        "diffsByCategory": {"categoryA": 0, "categoryB": 0, "categoryC": 0},
        "appliedDiffs": [],
        "stagedDiffs": [],
        "inlineOnlyDiffs": [],
    }
    if extra:
        doc.update(extra)
    return doc


def _minimal_diff(extras=None):
    diff = {
        "findingId": "F1-1",
        "findingCategory": "A",
        "confidence": 0.85,
        "targetFile": "src/x.ts",
    }
    if extras:
        diff.update(extras)
    return diff


class TestRemediateV07MigrationKind(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_migrationKind_field_declared_on_diff(self):
        diff_props = self.schema["$defs"]["diff"]["properties"]
        self.assertIn("migrationKind", diff_props)

    def test_migrationKind_enum(self):
        diff_props = self.schema["$defs"]["diff"]["properties"]
        enum_vals = diff_props["migrationKind"]["enum"]
        for expected in [
            "D-1-inline-to-registry",
            "D-2-typed-renderer",
            "D-3-model-consolidation",
        ]:
            self.assertIn(expected, enum_vals)

    def test_migrationKind_is_optional(self):
        required = self.schema["$defs"]["diff"].get("required", [])
        self.assertNotIn("migrationKind", required)

    def test_diff_with_D1_migrationKind_validates(self):
        doc = _minimal_remediate_result(
            extra={
                "appliedDiffs": [
                    _minimal_diff(
                        {"migrationKind": "D-1-inline-to-registry"}
                    )
                ]
            }
        )
        validate(instance=doc, schema=self.schema)

    def test_diff_with_invalid_migrationKind_rejected(self):
        doc = _minimal_remediate_result(
            extra={
                "appliedDiffs": [
                    _minimal_diff({"migrationKind": "D-9-undefined"})
                ]
            }
        )
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)


class TestRemediateV07ConsolidatedDiffs(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_consolidatedDiffs_top_level_field_declared(self):
        self.assertIn("consolidatedDiffs", self.schema["properties"])

    def test_consolidatedDiffs_is_array(self):
        cd = self.schema["properties"]["consolidatedDiffs"]
        self.assertEqual(cd["type"], "array")

    def test_consolidatedDiffs_item_required_fields(self):
        item = self.schema["properties"]["consolidatedDiffs"]["items"]
        for expected in ["path", "findingIds", "rationale"]:
            self.assertIn(expected, item["properties"])

    def test_consolidatedDiffs_findingIds_is_string_array(self):
        item = self.schema["properties"]["consolidatedDiffs"]["items"]
        self.assertEqual(item["properties"]["findingIds"]["type"], "array")
        self.assertEqual(
            item["properties"]["findingIds"]["items"]["type"], "string"
        )

    def test_remediate_with_consolidated_diffs_validates(self):
        doc = _minimal_remediate_result(
            extra={
                "consolidatedDiffs": [
                    {
                        "path": "src/prompts/registry.ts",
                        "findingIds": ["F10-1", "F11-1"],
                        "rationale": "F10 defense block also satisfies F11 phrase count.",
                    }
                ]
            }
        )
        validate(instance=doc, schema=self.schema)


class TestRemediateV07BackwardCompat(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_v06_remediate_result_validates(self):
        doc = {
            "runId": "r-2026-05-29-abc",
            "timestamp": "2026-05-29T18:00:00Z",
            "auditRunId": "a-2026-05-29-xyz",
            "totalFindings": 4,
            "diffsByCategory": {
                "categoryA": 1,
                "categoryB": 1,
                "categoryC": 1,
            },
            "appliedDiffs": [
                {
                    "findingId": "F1-1",
                    "findingCategory": "A",
                    "confidence": 0.92,
                    "targetFile": "src/x.ts",
                    "appliedAt": "2026-05-29T18:00:01Z",
                }
            ],
            "stagedDiffs": [
                {
                    "findingId": "F4-1",
                    "findingCategory": "B",
                    "subCategory": "voice-frame-rewrite",
                    "confidence": 0.75,
                    "targetFile": "src/prompts/registry.ts",
                    "stagedPath": ".vibe-prompt/remediate/pending/abc.diff",
                }
            ],
            "inlineOnlyDiffs": [],
            "f12HandoffsEmitted": [
                {
                    "promptId": "synastry",
                    "composerPath": "src/lib/gemini.ts",
                    "severity": "critical",
                    "autoHandoffInvoked": True,
                    "vibeSecResultPath": ".vibe-prompt/remediate/handoff-vibe-sec-2026-05-29.json",
                }
            ],
            "flags": {
                "autoApply": False,
                "interactive": False,
                "skipF12": False,
                "applyContradictions": True,
            },
        }
        validate(instance=doc, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
