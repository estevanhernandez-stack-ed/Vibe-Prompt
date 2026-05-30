"""
Task 6 (v0.6) — TDD tests for NEW handoff-vibe-sec.schema.json.

Asserts (per spec §3 schema definition):
  1. Required: runId, timestamp, triggeringFinding, vibeSecVersion,
     vibeSecFindings, exitCode.
  2. runId string, timestamp date-time, triggeringFinding string,
     vibeSecVersion string, vibeSecFindings array, exitCode integer.
  3. scope optional string.
  4. Spec §3 sample doc validates.
  5. Missing required fields rejected.
"""

import json
import pathlib
import unittest

from jsonschema import validate, ValidationError

SCHEMAS_DIR = pathlib.Path(__file__).parent.parent.parent / "schemas"
HANDOFF_SCHEMA_PATH = SCHEMAS_DIR / "handoff-vibe-sec.schema.json"


def load_schema():
    with open(HANDOFF_SCHEMA_PATH) as f:
        return json.load(f)


class TestHandoffVibeSecSchemaStructure(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_schema_is_object(self):
        self.assertEqual(self.schema["type"], "object")

    def test_required_fields(self):
        required = self.schema.get("required", [])
        for field in [
            "runId",
            "timestamp",
            "triggeringFinding",
            "vibeSecVersion",
            "vibeSecFindings",
            "exitCode",
        ]:
            self.assertIn(field, required, f"required field {field} missing")

    def test_runId_is_string(self):
        self.assertEqual(self.schema["properties"]["runId"]["type"], "string")

    def test_timestamp_is_date_time(self):
        ts = self.schema["properties"]["timestamp"]
        self.assertEqual(ts["type"], "string")
        self.assertEqual(ts["format"], "date-time")

    def test_triggeringFinding_is_string(self):
        self.assertEqual(
            self.schema["properties"]["triggeringFinding"]["type"], "string"
        )

    def test_vibeSecVersion_is_string(self):
        self.assertEqual(
            self.schema["properties"]["vibeSecVersion"]["type"], "string"
        )

    def test_vibeSecFindings_is_array(self):
        self.assertEqual(
            self.schema["properties"]["vibeSecFindings"]["type"], "array"
        )

    def test_exitCode_is_integer(self):
        self.assertEqual(
            self.schema["properties"]["exitCode"]["type"], "integer"
        )

    def test_scope_is_optional_string(self):
        self.assertIn("scope", self.schema["properties"])
        self.assertEqual(self.schema["properties"]["scope"]["type"], "string")
        required = self.schema.get("required", [])
        self.assertNotIn("scope", required)


class TestHandoffVibeSecSampleDocs(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_spec_sample_validates(self):
        # Verbatim from spec §3
        doc = {
            "runId": "handoff-2026-06-15-1430",
            "timestamp": "2026-06-15T14:30:00Z",
            "triggeringFinding": "F12-inline_oneirocriton-2026-06-15",
            "vibeSecVersion": "0.6.0",
            "vibeSecFindings": [],
            "exitCode": 0,
            "scope": "user-input-boundary",
        }
        validate(instance=doc, schema=self.schema)

    def test_minimal_required_doc_validates(self):
        doc = {
            "runId": "handoff-1",
            "timestamp": "2026-06-15T14:30:00Z",
            "triggeringFinding": "F12-x",
            "vibeSecVersion": "0.6.0",
            "vibeSecFindings": [],
            "exitCode": 0,
        }
        validate(instance=doc, schema=self.schema)

    def test_doc_with_findings_validates(self):
        doc = {
            "runId": "handoff-2",
            "timestamp": "2026-06-15T14:30:00Z",
            "triggeringFinding": "F12-y",
            "vibeSecVersion": "0.6.1",
            "vibeSecFindings": [
                {"id": "VS-1", "severity": "high"},
                {"id": "VS-2", "severity": "medium"},
            ],
            "exitCode": 1,
            "scope": "user-input-boundary",
        }
        validate(instance=doc, schema=self.schema)

    def test_doc_missing_runId_rejected(self):
        doc = {
            "timestamp": "2026-06-15T14:30:00Z",
            "triggeringFinding": "F12-x",
            "vibeSecVersion": "0.6.0",
            "vibeSecFindings": [],
            "exitCode": 0,
        }
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)

    def test_doc_missing_vibeSecFindings_rejected(self):
        doc = {
            "runId": "handoff-1",
            "timestamp": "2026-06-15T14:30:00Z",
            "triggeringFinding": "F12-x",
            "vibeSecVersion": "0.6.0",
            "exitCode": 0,
        }
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)

    def test_doc_with_non_integer_exitCode_rejected(self):
        doc = {
            "runId": "handoff-1",
            "timestamp": "2026-06-15T14:30:00Z",
            "triggeringFinding": "F12-x",
            "vibeSecVersion": "0.6.0",
            "vibeSecFindings": [],
            "exitCode": "zero",
        }
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
