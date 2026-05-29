"""
Task 5 — TDD tests for NEW remediate-result.schema.json + pending-fix.schema.json.

Asserts:
  remediate-result:
    1. required: runId, timestamp, auditRunId, totalFindings, diffsByCategory,
       appliedDiffs, stagedDiffs, inlineOnlyDiffs
    2. diffsByCategory has categoryA / categoryB / categoryC integers
    3. *Diffs arrays (applied / staged / inlineOnly) accept diff objects
    4. f12HandoffsEmitted optional array; backupBatchPath optional string
    5. Spec §1d sample doc validates
  pending-fix (front-matter):
    1. required: findingId, findingCategory, confidence, targetFile, targetRange,
       recommendationSource
    2. findingCategory enum A | B | C
    3. confidence number 0-1
    4. versionBumpRequired optional boolean
    5. Spec §1d sample front-matter validates
"""

import json
import pathlib
import unittest

from jsonschema import validate, ValidationError

SCHEMAS_DIR = pathlib.Path(__file__).parent.parent.parent / "schemas"
REMEDIATE_RESULT_PATH = SCHEMAS_DIR / "remediate-result.schema.json"
PENDING_FIX_PATH = SCHEMAS_DIR / "pending-fix.schema.json"


def load_schema(path):
    with open(path) as f:
        return json.load(f)


# ---------- remediate-result ---------- #

class TestRemediateResultSchemaStructure(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema(REMEDIATE_RESULT_PATH)

    def test_required_top_level_fields(self):
        required = self.schema.get("required", [])
        for field in [
            "runId",
            "timestamp",
            "auditRunId",
            "totalFindings",
            "diffsByCategory",
            "appliedDiffs",
            "stagedDiffs",
            "inlineOnlyDiffs",
        ]:
            self.assertIn(field, required, f"required field {field} missing")

    def test_runId_is_string(self):
        self.assertEqual(self.schema["properties"]["runId"]["type"], "string")

    def test_timestamp_is_date_time(self):
        ts = self.schema["properties"]["timestamp"]
        self.assertEqual(ts["type"], "string")
        self.assertEqual(ts["format"], "date-time")

    def test_totalFindings_is_integer(self):
        self.assertEqual(
            self.schema["properties"]["totalFindings"]["type"], "integer"
        )

    def test_diffsByCategory_has_three_categories(self):
        dbc = self.schema["properties"]["diffsByCategory"]["properties"]
        self.assertEqual(dbc["categoryA"]["type"], "integer")
        self.assertEqual(dbc["categoryB"]["type"], "integer")
        self.assertEqual(dbc["categoryC"]["type"], "integer")

    def test_appliedDiffs_is_array(self):
        self.assertEqual(self.schema["properties"]["appliedDiffs"]["type"], "array")

    def test_stagedDiffs_is_array(self):
        self.assertEqual(self.schema["properties"]["stagedDiffs"]["type"], "array")

    def test_inlineOnlyDiffs_is_array(self):
        self.assertEqual(
            self.schema["properties"]["inlineOnlyDiffs"]["type"], "array"
        )

    def test_f12HandoffsEmitted_field_exists(self):
        self.assertIn("f12HandoffsEmitted", self.schema["properties"])

    def test_backupBatchPath_field_exists(self):
        self.assertIn("backupBatchPath", self.schema["properties"])


class TestRemediateResultSampleDocs(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema(REMEDIATE_RESULT_PATH)

    def test_spec_sample_validates(self):
        doc = {
            "runId": "remediate-2026-05-30-0900",
            "timestamp": "2026-05-30T09:00:00Z",
            "auditRunId": "audit-2026-05-29-1830",
            "totalFindings": 7,
            "diffsByCategory": {"categoryA": 1, "categoryB": 2, "categoryC": 4},
            "appliedDiffs": [],
            "stagedDiffs": [],
            "inlineOnlyDiffs": [],
            "f12HandoffsEmitted": [],
            "backupBatchPath": ".vibe-prompt/remediate/backup/2026-05-30-0900/",
        }
        validate(instance=doc, schema=self.schema)

    def test_minimal_required_doc_validates(self):
        doc = {
            "runId": "r1",
            "timestamp": "2026-05-30T09:00:00Z",
            "auditRunId": "a1",
            "totalFindings": 0,
            "diffsByCategory": {"categoryA": 0, "categoryB": 0, "categoryC": 0},
            "appliedDiffs": [],
            "stagedDiffs": [],
            "inlineOnlyDiffs": [],
        }
        validate(instance=doc, schema=self.schema)

    def test_doc_missing_required_rejected(self):
        doc = {
            "runId": "r1",
            "timestamp": "2026-05-30T09:00:00Z",
            "auditRunId": "a1",
            # missing totalFindings, diffsByCategory, etc.
        }
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)

    def test_doc_with_diff_objects_validates(self):
        doc = {
            "runId": "r1",
            "timestamp": "2026-05-30T09:00:00Z",
            "auditRunId": "a1",
            "totalFindings": 3,
            "diffsByCategory": {"categoryA": 1, "categoryB": 1, "categoryC": 1},
            "appliedDiffs": [
                {
                    "findingId": "F9-natal-2026-05-29",
                    "findingCategory": "A",
                    "confidence": 0.95,
                    "targetFile": "src/lib/gemini.ts",
                }
            ],
            "stagedDiffs": [
                {
                    "findingId": "F2-natal-2026-05-29",
                    "findingCategory": "B",
                    "confidence": 0.75,
                    "targetFile": "src/lib/ConfigService.ts",
                }
            ],
            "inlineOnlyDiffs": [],
        }
        validate(instance=doc, schema=self.schema)


# ---------- pending-fix front-matter ---------- #

class TestPendingFixSchemaStructure(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema(PENDING_FIX_PATH)

    def test_required_fields(self):
        required = self.schema.get("required", [])
        for field in [
            "findingId",
            "findingCategory",
            "confidence",
            "targetFile",
            "targetRange",
            "recommendationSource",
        ]:
            self.assertIn(field, required, f"required field {field} missing")

    def test_findingCategory_enum(self):
        enum_vals = self.schema["properties"]["findingCategory"]["enum"]
        self.assertIn("A", enum_vals)
        self.assertIn("B", enum_vals)
        self.assertIn("C", enum_vals)

    def test_confidence_is_number_range(self):
        c = self.schema["properties"]["confidence"]
        self.assertEqual(c["type"], "number")
        self.assertEqual(c["minimum"], 0)
        self.assertEqual(c["maximum"], 1)

    def test_findingId_is_string(self):
        self.assertEqual(self.schema["properties"]["findingId"]["type"], "string")

    def test_targetFile_is_string(self):
        self.assertEqual(self.schema["properties"]["targetFile"]["type"], "string")

    def test_targetRange_is_string(self):
        self.assertEqual(self.schema["properties"]["targetRange"]["type"], "string")

    def test_recommendationSource_is_string(self):
        self.assertEqual(
            self.schema["properties"]["recommendationSource"]["type"], "string"
        )

    def test_versionBumpRequired_optional_boolean(self):
        self.assertIn("versionBumpRequired", self.schema["properties"])
        self.assertEqual(
            self.schema["properties"]["versionBumpRequired"]["type"], "boolean"
        )
        self.assertNotIn(
            "versionBumpRequired", self.schema.get("required", [])
        )

    def test_suggestedVersion_optional(self):
        self.assertIn("suggestedVersion", self.schema["properties"])
        self.assertNotIn("suggestedVersion", self.schema.get("required", []))

    def test_backupPath_optional(self):
        self.assertIn("backupPath", self.schema["properties"])
        self.assertNotIn("backupPath", self.schema.get("required", []))

    def test_postApplyRecommendation_optional(self):
        self.assertIn("postApplyRecommendation", self.schema["properties"])
        self.assertNotIn(
            "postApplyRecommendation", self.schema.get("required", [])
        )


class TestPendingFixSampleDocs(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema(PENDING_FIX_PATH)

    def test_spec_sample_front_matter_validates(self):
        doc = {
            "findingId": "F2-natal_interpretation-2026-05-29",
            "findingCategory": "B",
            "confidence": 0.75,
            "targetFile": "src/lib/ConfigService.ts",
            "targetRange": "L67-L102",
            "backupPath": ".vibe-prompt/remediate/backup/2026-05-30-0900/ConfigService.ts.bak",
            "recommendationSource": "audit-2026-05-29-1830",
            "postApplyRecommendation": "Re-run /vibe-prompt:eval --prompts natal_interpretation",
            "versionBumpRequired": True,
            "suggestedVersion": "3.6.0",
        }
        validate(instance=doc, schema=self.schema)

    def test_minimal_required_pending_validates(self):
        doc = {
            "findingId": "F10-oneirocriton-2026-05-29",
            "findingCategory": "C",
            "confidence": 0.78,
            "targetFile": "src/Oneirocriton.tsx",
            "targetRange": "L72-L95",
            "recommendationSource": "audit-2026-05-29-1830",
        }
        validate(instance=doc, schema=self.schema)

    def test_invalid_findingCategory_rejected(self):
        doc = {
            "findingId": "F9-x-2026-05-29",
            "findingCategory": "Z",
            "confidence": 0.9,
            "targetFile": "x.ts",
            "targetRange": "L1-L2",
            "recommendationSource": "a",
        }
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)

    def test_confidence_above_1_rejected(self):
        doc = {
            "findingId": "F9-x-2026-05-29",
            "findingCategory": "A",
            "confidence": 1.5,
            "targetFile": "x.ts",
            "targetRange": "L1-L2",
            "recommendationSource": "a",
        }
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)

    def test_missing_required_field_rejected(self):
        doc = {
            "findingId": "F9-x-2026-05-29",
            "findingCategory": "A",
            # missing confidence + targetFile + targetRange + recommendationSource
        }
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
