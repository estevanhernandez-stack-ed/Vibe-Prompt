"""
Task 3 (v0.6) — TDD tests for remediate-result.schema.json v0.6 extensions.

Asserts:
  1. appliedDiffs[].subCategory optional string
  2. f12HandoffsEmitted[].autoHandoffInvoked optional boolean
  3. f12HandoffsEmitted[].vibeSecResultPath optional string
  4. Backward compat: v0.5 remediate-result.json validates
"""

import json
import pathlib
import unittest

from jsonschema import validate, ValidationError

SCHEMAS_DIR = pathlib.Path(__file__).parent.parent.parent / "schemas"
REMEDIATE_RESULT_PATH = SCHEMAS_DIR / "remediate-result.schema.json"


def load_schema():
    with open(REMEDIATE_RESULT_PATH) as f:
        return json.load(f)


def _minimal_doc(extra=None):
    doc = {
        "runId": "remediate-2026-06-15-1430",
        "timestamp": "2026-06-15T14:30:00Z",
        "auditRunId": "audit-2026-06-15-1400",
        "totalFindings": 0,
        "diffsByCategory": {"categoryA": 0, "categoryB": 0, "categoryC": 0},
        "appliedDiffs": [],
        "stagedDiffs": [],
        "inlineOnlyDiffs": [],
    }
    if extra:
        doc.update(extra)
    return doc


class TestRemediateV06SubCategory(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_subCategory_field_exists_on_diff(self):
        diff_props = self.schema["$defs"]["diff"]["properties"]
        self.assertIn("subCategory", diff_props)

    def test_subCategory_accepts_string(self):
        """v0.7 widened type to [string, null] for v0.6 back-compat; string is still valid."""
        diff_props = self.schema["$defs"]["diff"]["properties"]
        sub_cat_type = diff_props["subCategory"]["type"]
        if isinstance(sub_cat_type, list):
            self.assertIn("string", sub_cat_type)
        else:
            self.assertEqual(sub_cat_type, "string")

    def test_subCategory_is_optional(self):
        required = self.schema["$defs"]["diff"].get("required", [])
        self.assertNotIn("subCategory", required)

    def test_applied_diff_with_subCategory_validates(self):
        doc = _minimal_doc(
            {
                "totalFindings": 1,
                "diffsByCategory": {"categoryA": 0, "categoryB": 1, "categoryC": 0},
                "appliedDiffs": [
                    {
                        "findingId": "F2-natal-2026-06-15",
                        "findingCategory": "B",
                        "subCategory": "voice-frame-rewrite",
                        "confidence": 0.65,
                        "targetFile": "src/lib/ConfigService.ts",
                    }
                ],
            }
        )
        validate(instance=doc, schema=self.schema)

    def test_applied_diff_with_banned_phrase_subCategory_validates(self):
        doc = _minimal_doc(
            {
                "totalFindings": 1,
                "diffsByCategory": {"categoryA": 0, "categoryB": 1, "categoryC": 0},
                "appliedDiffs": [
                    {
                        "findingId": "F2-natal-2026-06-15",
                        "findingCategory": "B",
                        "subCategory": "banned-phrase-removal",
                        "confidence": 0.75,
                        "targetFile": "src/lib/ConfigService.ts",
                    }
                ],
            }
        )
        validate(instance=doc, schema=self.schema)


class TestRemediateV06AutoHandoffFields(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_autoHandoffInvoked_field_exists_on_f12Handoff(self):
        handoff_props = self.schema["$defs"]["f12Handoff"]["properties"]
        self.assertIn("autoHandoffInvoked", handoff_props)

    def test_autoHandoffInvoked_is_boolean(self):
        handoff_props = self.schema["$defs"]["f12Handoff"]["properties"]
        self.assertEqual(handoff_props["autoHandoffInvoked"]["type"], "boolean")

    def test_autoHandoffInvoked_is_optional(self):
        required = self.schema["$defs"]["f12Handoff"].get("required", [])
        self.assertNotIn("autoHandoffInvoked", required)

    def test_vibeSecResultPath_field_exists_on_f12Handoff(self):
        handoff_props = self.schema["$defs"]["f12Handoff"]["properties"]
        self.assertIn("vibeSecResultPath", handoff_props)

    def test_vibeSecResultPath_is_string(self):
        handoff_props = self.schema["$defs"]["f12Handoff"]["properties"]
        self.assertEqual(handoff_props["vibeSecResultPath"]["type"], "string")

    def test_vibeSecResultPath_is_optional(self):
        required = self.schema["$defs"]["f12Handoff"].get("required", [])
        self.assertNotIn("vibeSecResultPath", required)

    def test_f12Handoff_with_auto_handoff_fields_validates(self):
        doc = _minimal_doc(
            {
                "f12HandoffsEmitted": [
                    {
                        "promptId": "oneirocriton",
                        "composerPath": ".vibe-prompt/composer.json",
                        "banner": "F12 critical: ...",
                        "severity": "critical",
                        "autoHandoffInvoked": True,
                        "vibeSecResultPath": ".vibe-prompt/remediate/state/handoff-vibe-sec-2026-06-15-1430.json",
                    }
                ]
            }
        )
        validate(instance=doc, schema=self.schema)

    def test_f12Handoff_with_auto_handoff_false_validates(self):
        doc = _minimal_doc(
            {
                "f12HandoffsEmitted": [
                    {
                        "promptId": "oneirocriton",
                        "composerPath": ".vibe-prompt/composer.json",
                        "autoHandoffInvoked": False,
                    }
                ]
            }
        )
        validate(instance=doc, schema=self.schema)


class TestRemediateV06BackwardCompat(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_v05_minimal_doc_validates(self):
        doc = _minimal_doc()
        validate(instance=doc, schema=self.schema)

    def test_v05_diff_without_subCategory_validates(self):
        doc = _minimal_doc(
            {
                "totalFindings": 1,
                "diffsByCategory": {"categoryA": 1, "categoryB": 0, "categoryC": 0},
                "appliedDiffs": [
                    {
                        "findingId": "F9-natal-2026-05-29",
                        "findingCategory": "A",
                        "confidence": 0.95,
                        "targetFile": "src/lib/gemini.ts",
                    }
                ],
            }
        )
        validate(instance=doc, schema=self.schema)

    def test_v05_f12Handoff_without_auto_handoff_fields_validates(self):
        doc = _minimal_doc(
            {
                "f12HandoffsEmitted": [
                    {
                        "promptId": "oneirocriton",
                        "composerPath": ".vibe-prompt/composer.json",
                        "banner": "F12 critical: ...",
                        "severity": "critical",
                    }
                ]
            }
        )
        validate(instance=doc, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
