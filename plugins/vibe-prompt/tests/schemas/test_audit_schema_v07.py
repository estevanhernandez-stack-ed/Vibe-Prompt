"""
Task 3 (v0.7) — TDD tests for audit.schema.json v0.7 extensions.

Asserts:
  1. findings[].composerIdentifier optional string
  2. findings[].workspaceIdentifier optional string
  3. findings[].consolidatedWith optional array of finding-id strings
  4. findings[].id enum gains F6-suspect-model
  5. Backward compat: v0.6 audit.json (no composer/workspace identifiers,
     no consolidatedWith) validates
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


def _minimal_audit(finding_extras=None):
    finding = {
        "id": "F1",
        "smell": "bypassed-registry",
        "severity": "high",
        "evidence": [{"file": "x.ts", "line": 1}],
        "recommendation": "Move to registry.",
    }
    if finding_extras:
        finding.update(finding_extras)
    return {
        "version": "0.1",
        "auditedAt": "2026-06-01T00:00:00Z",
        "inventoryRef": ".vibe-prompt/state/inventory.json",
        "findings": [finding],
        "summary": {"totalFindings": 1, "byCategory": {"high": 1}},
    }


class TestAuditV07ComposerIdentifier(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_composerIdentifier_property_declared(self):
        finding_props = self.schema["properties"]["findings"]["items"]["properties"]
        self.assertIn("composerIdentifier", finding_props)

    def test_composerIdentifier_is_string_or_null(self):
        finding_props = self.schema["properties"]["findings"]["items"]["properties"]
        ci = finding_props["composerIdentifier"]
        # Either type: ["string", "null"] OR oneOf-style
        types = ci.get("type")
        if isinstance(types, list):
            self.assertIn("string", types)
            self.assertIn("null", types)
        else:
            self.assertEqual(types, "string")

    def test_finding_with_composerIdentifier_validates(self):
        doc = _minimal_audit(
            finding_extras={"composerIdentifier": "src/galaxyCore.ts"}
        )
        validate(instance=doc, schema=self.schema)

    def test_finding_with_null_composerIdentifier_validates(self):
        doc = _minimal_audit(finding_extras={"composerIdentifier": None})
        validate(instance=doc, schema=self.schema)


class TestAuditV07WorkspaceIdentifier(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_workspaceIdentifier_property_declared(self):
        finding_props = self.schema["properties"]["findings"]["items"]["properties"]
        self.assertIn("workspaceIdentifier", finding_props)

    def test_finding_with_workspaceIdentifier_validates(self):
        doc = _minimal_audit(finding_extras={"workspaceIdentifier": "cinema"})
        validate(instance=doc, schema=self.schema)

    def test_finding_with_null_workspaceIdentifier_validates(self):
        doc = _minimal_audit(finding_extras={"workspaceIdentifier": None})
        validate(instance=doc, schema=self.schema)


class TestAuditV07ConsolidatedWith(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_consolidatedWith_property_declared(self):
        finding_props = self.schema["properties"]["findings"]["items"]["properties"]
        self.assertIn("consolidatedWith", finding_props)

    def test_consolidatedWith_is_array_of_strings(self):
        finding_props = self.schema["properties"]["findings"]["items"]["properties"]
        cw = finding_props["consolidatedWith"]
        self.assertEqual(cw["type"], "array")
        self.assertEqual(cw["items"]["type"], "string")

    def test_finding_with_consolidatedWith_validates(self):
        doc = _minimal_audit(
            finding_extras={"consolidatedWith": ["F11-1", "F12-1"]}
        )
        validate(instance=doc, schema=self.schema)


class TestAuditV07F6SuspectModel(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_F6_suspect_model_in_id_enum(self):
        id_enum = self.schema["properties"]["findings"]["items"]["properties"]["id"][
            "enum"
        ]
        self.assertIn("F6-suspect-model", id_enum)

    def test_existing_ids_preserved(self):
        id_enum = self.schema["properties"]["findings"]["items"]["properties"]["id"][
            "enum"
        ]
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
            "F13",
        ]:
            self.assertIn(expected, id_enum)

    def test_finding_with_F6_suspect_model_validates(self):
        doc = _minimal_audit(
            finding_extras={
                "id": "F6-suspect-model",
                "smell": "suspect-model-id",
                "severity": "medium",
                "evidence": [{"file": "x.ts", "line": 1}],
                "recommendation": "Verify the model id.",
            }
        )
        doc["findings"][0] = {
            "id": "F6-suspect-model",
            "smell": "suspect-model-id",
            "severity": "medium",
            "evidence": [{"file": "x.ts", "line": 1}],
            "recommendation": "Verify the model id.",
        }
        validate(instance=doc, schema=self.schema)


class TestAuditV07BackwardCompat(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_v06_audit_validates(self):
        doc = {
            "version": "0.1",
            "auditedAt": "2026-05-29T00:00:00Z",
            "inventoryRef": ".vibe-prompt/state/inventory.json",
            "findings": [
                {
                    "id": "F1",
                    "smell": "bypassed-registry",
                    "severity": "high",
                    "evidence": [{"file": "src/x.ts", "line": 10}],
                    "recommendation": "Move inline prompt to registry.",
                },
                {
                    "id": "F12",
                    "smell": "structural-injection-vector",
                    "severity": "critical",
                    "evidence": [{"file": "src/y.ts", "line": 22}],
                    "recommendation": "Move user var to contents[].",
                    "apiParameterContext": {
                        "userVarApiParameter": "systemInstruction",
                        "systemInstructionApiParameter": "systemInstruction",
                        "separationVerified": False,
                    },
                },
            ],
            "summary": {
                "totalFindings": 2,
                "byCategory": {"high": 1, "critical": 1},
            },
        }
        validate(instance=doc, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
