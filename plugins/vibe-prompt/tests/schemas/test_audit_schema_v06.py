"""
Task 2 (v0.6) — TDD tests for audit.schema.json v0.6 extensions.

Asserts:
  1. findings[].id enum includes F13
  2. findings[].apiParameterContext optional object with
     {userVarApiParameter, systemInstructionApiParameter, separationVerified}
  3. findings[].voiceFrameContradictions optional array of
     {phrase, location, banSource}
  4. Backward compat: v0.5 audit.json validates
"""

import json
import pathlib
import unittest

from jsonschema import validate, ValidationError

SCHEMAS_DIR = pathlib.Path(__file__).parent.parent.parent / "schemas"
AUDIT_SCHEMA_PATH = SCHEMAS_DIR / "audit.schema.json"


def load_schema():
    with open(AUDIT_SCHEMA_PATH) as f:
        return json.load(f)


def _minimal_finding(extra=None, fid="F10"):
    f = {
        "id": fid,
        "smell": "User-input var without sanitization",
        "severity": "high",
        "evidence": [{"file": "src/x.tsx", "line": 10}],
        "recommendation": "Add defense block",
    }
    if extra:
        f.update(extra)
    return f


def _minimal_doc(finding):
    return {
        "version": "0.1",
        "auditedAt": "2026-06-15T09:00:00Z",
        "inventoryRef": "inventory.json",
        "findings": [finding],
        "summary": {"totalFindings": 1, "byCategory": {"high": 1}},
    }


class TestAuditV06F13EnumExtension(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_F13_in_id_enum(self):
        finding_props = self.schema["properties"]["findings"]["items"]["properties"]
        enum_vals = finding_props["id"]["enum"]
        self.assertIn("F13", enum_vals)

    def test_existing_F_ids_preserved(self):
        finding_props = self.schema["properties"]["findings"]["items"]["properties"]
        enum_vals = finding_props["id"]["enum"]
        for expected in [
            "F1",
            "F1b",
            "F2",
            "F3",
            "F4",
            "F5",
            "F6",
            "F7",
            "F9",
            "F10",
            "F11",
            "F12",
        ]:
            self.assertIn(expected, enum_vals)

    def test_finding_with_F13_validates(self):
        doc = _minimal_doc(
            _minimal_finding(
                {"smell": "Implicit output format", "severity": "medium"}, fid="F13"
            )
        )
        validate(instance=doc, schema=self.schema)

    def test_finding_with_F14_rejected(self):
        doc = _minimal_doc(_minimal_finding(fid="F14"))
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)


class TestAuditV06ApiParameterContext(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_apiParameterContext_field_exists(self):
        finding_props = self.schema["properties"]["findings"]["items"]["properties"]
        self.assertIn("apiParameterContext", finding_props)

    def test_apiParameterContext_is_object(self):
        finding_props = self.schema["properties"]["findings"]["items"]["properties"]
        self.assertEqual(finding_props["apiParameterContext"]["type"], "object")

    def test_apiParameterContext_is_optional(self):
        required = self.schema["properties"]["findings"]["items"].get("required", [])
        self.assertNotIn("apiParameterContext", required)

    def test_apiParameterContext_has_three_fields(self):
        finding_props = self.schema["properties"]["findings"]["items"]["properties"]
        apc_props = finding_props["apiParameterContext"]["properties"]
        self.assertIn("userVarApiParameter", apc_props)
        self.assertIn("systemInstructionApiParameter", apc_props)
        self.assertIn("separationVerified", apc_props)

    def test_separationVerified_is_boolean(self):
        finding_props = self.schema["properties"]["findings"]["items"]["properties"]
        apc_props = finding_props["apiParameterContext"]["properties"]
        self.assertEqual(apc_props["separationVerified"]["type"], "boolean")

    def test_finding_with_apiParameterContext_validates(self):
        doc = _minimal_doc(
            _minimal_finding(
                {
                    "apiParameterContext": {
                        "userVarApiParameter": "contents",
                        "systemInstructionApiParameter": "systemInstruction",
                        "separationVerified": True,
                    }
                },
                fid="F12",
            )
        )
        validate(instance=doc, schema=self.schema)

    def test_finding_with_separationVerified_false_validates(self):
        doc = _minimal_doc(
            _minimal_finding(
                {
                    "apiParameterContext": {
                        "userVarApiParameter": "systemInstruction",
                        "systemInstructionApiParameter": "systemInstruction",
                        "separationVerified": False,
                    }
                },
                fid="F12",
            )
        )
        validate(instance=doc, schema=self.schema)


class TestAuditV06VoiceFrameContradictions(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_voiceFrameContradictions_field_exists(self):
        finding_props = self.schema["properties"]["findings"]["items"]["properties"]
        self.assertIn("voiceFrameContradictions", finding_props)

    def test_voiceFrameContradictions_is_array(self):
        finding_props = self.schema["properties"]["findings"]["items"]["properties"]
        self.assertEqual(
            finding_props["voiceFrameContradictions"]["type"], "array"
        )

    def test_voiceFrameContradictions_is_optional(self):
        required = self.schema["properties"]["findings"]["items"].get("required", [])
        self.assertNotIn("voiceFrameContradictions", required)

    def test_voiceFrameContradictions_items_have_three_fields(self):
        finding_props = self.schema["properties"]["findings"]["items"]["properties"]
        item_props = finding_props["voiceFrameContradictions"]["items"]["properties"]
        self.assertIn("phrase", item_props)
        self.assertIn("location", item_props)
        self.assertIn("banSource", item_props)

    def test_finding_with_voiceFrameContradictions_validates(self):
        doc = _minimal_doc(
            _minimal_finding(
                {
                    "voiceFrameContradictions": [
                        {
                            "phrase": "quatrain-style narrative",
                            "location": "natal_interpretation:L42",
                            "banSource": "global-directive: plain modern language",
                        },
                        {
                            "phrase": "shattering of the veil",
                            "location": "natal_interpretation:L67",
                            "banSource": "global-directive: not a 16th-century prophet",
                        },
                    ]
                },
                fid="F2",
            )
        )
        validate(instance=doc, schema=self.schema)

    def test_finding_with_empty_voiceFrameContradictions_validates(self):
        doc = _minimal_doc(
            _minimal_finding({"voiceFrameContradictions": []}, fid="F2")
        )
        validate(instance=doc, schema=self.schema)


class TestAuditV06BackwardCompat(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_v05_finding_without_new_fields_validates(self):
        doc = _minimal_doc(_minimal_finding())
        validate(instance=doc, schema=self.schema)

    def test_v05_finding_with_handoffHint_and_varOriginUsed(self):
        doc = _minimal_doc(
            _minimal_finding(
                {
                    "handoffHint": "vibe-sec:audit",
                    "originFilteredOut": False,
                    "varOriginUsed": "user-controlled",
                }
            )
        )
        validate(instance=doc, schema=self.schema)

    def test_v06_finding_with_all_new_fields_validates(self):
        doc = _minimal_doc(
            _minimal_finding(
                {
                    "handoffHint": "vibe-sec:audit",
                    "originFilteredOut": False,
                    "varOriginUsed": "user-controlled",
                    "apiParameterContext": {
                        "userVarApiParameter": "contents",
                        "systemInstructionApiParameter": "systemInstruction",
                        "separationVerified": True,
                    },
                    "voiceFrameContradictions": [
                        {
                            "phrase": "ancient dust",
                            "location": "natal:L88",
                            "banSource": "global-directive",
                        }
                    ],
                },
                fid="F12",
            )
        )
        validate(instance=doc, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
