"""
Task 3 — TDD tests for audit.schema.json v0.5 extensions.

Asserts:
  1. findings[].originFilteredOut optional boolean
  2. findings[].varOriginUsed optional enum (user-controlled | system-injected | unknown)
  3. Backward compat: v0.4 audit.json still validates
  4. New fields are not required
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


def _minimal_finding(extra=None):
    f = {
        "id": "F10",
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
        "auditedAt": "2026-05-30T09:00:00Z",
        "inventoryRef": "inventory.json",
        "findings": [finding],
        "summary": {"totalFindings": 1, "byCategory": {"high": 1}},
    }


class TestAuditV05OriginFilteredOut(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_originFilteredOut_field_exists(self):
        finding_props = self.schema["properties"]["findings"]["items"]["properties"]
        self.assertIn("originFilteredOut", finding_props)

    def test_originFilteredOut_is_boolean(self):
        finding_props = self.schema["properties"]["findings"]["items"]["properties"]
        self.assertEqual(finding_props["originFilteredOut"]["type"], "boolean")

    def test_originFilteredOut_is_optional(self):
        required = self.schema["properties"]["findings"]["items"].get("required", [])
        self.assertNotIn("originFilteredOut", required)

    def test_finding_with_originFilteredOut_true_validates(self):
        doc = _minimal_doc(_minimal_finding({"originFilteredOut": True}))
        validate(instance=doc, schema=self.schema)

    def test_finding_with_originFilteredOut_false_validates(self):
        doc = _minimal_doc(_minimal_finding({"originFilteredOut": False}))
        validate(instance=doc, schema=self.schema)

    def test_finding_with_invalid_originFilteredOut_rejected(self):
        doc = _minimal_doc(_minimal_finding({"originFilteredOut": "maybe"}))
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)


class TestAuditV05VarOriginUsed(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_varOriginUsed_field_exists(self):
        finding_props = self.schema["properties"]["findings"]["items"]["properties"]
        self.assertIn("varOriginUsed", finding_props)

    def test_varOriginUsed_enum(self):
        finding_props = self.schema["properties"]["findings"]["items"]["properties"]
        enum_vals = finding_props["varOriginUsed"]["enum"]
        self.assertIn("user-controlled", enum_vals)
        self.assertIn("system-injected", enum_vals)
        self.assertIn("unknown", enum_vals)

    def test_varOriginUsed_is_optional(self):
        required = self.schema["properties"]["findings"]["items"].get("required", [])
        self.assertNotIn("varOriginUsed", required)

    def test_finding_with_varOriginUsed_user_controlled_validates(self):
        doc = _minimal_doc(
            _minimal_finding({"varOriginUsed": "user-controlled"})
        )
        validate(instance=doc, schema=self.schema)

    def test_finding_with_varOriginUsed_system_injected_validates(self):
        doc = _minimal_doc(
            _minimal_finding({"varOriginUsed": "system-injected"})
        )
        validate(instance=doc, schema=self.schema)

    def test_finding_with_varOriginUsed_unknown_validates(self):
        doc = _minimal_doc(_minimal_finding({"varOriginUsed": "unknown"}))
        validate(instance=doc, schema=self.schema)

    def test_finding_with_invalid_varOriginUsed_rejected(self):
        doc = _minimal_doc(_minimal_finding({"varOriginUsed": "alien"}))
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)


class TestAuditV05BackwardCompat(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_v04_finding_without_new_fields_validates(self):
        doc = _minimal_doc(_minimal_finding())
        validate(instance=doc, schema=self.schema)

    def test_v04_audit_with_handoffHint_validates(self):
        doc = _minimal_doc(_minimal_finding({"handoffHint": "vibe-sec:audit"}))
        validate(instance=doc, schema=self.schema)

    def test_v05_finding_with_all_new_fields_validates(self):
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


if __name__ == "__main__":
    unittest.main()
