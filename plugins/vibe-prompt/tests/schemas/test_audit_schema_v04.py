"""
Task 1 — TDD tests for audit.schema.json v0.4 extensions.

Asserts:
  1. findings[].id enum includes F9, F10, F11, F12
  2. findings[].handoffHint optional string field exists in schema
  3. auditGrade.perPrompt.dimensions.injectionResistance shape: {value: 1-10, rationale: string}
  4. auditGrade.suggestedWeightOverrides[] items include rationale (string) and appTypeSignal enum
  5. Backwards compat: a v0.3-style audit document still validates
"""

import json
import pathlib
import unittest

import jsonschema
from jsonschema import validate, ValidationError

SCHEMAS_DIR = pathlib.Path(__file__).parent.parent.parent / "schemas"
AUDIT_SCHEMA_PATH = SCHEMAS_DIR / "audit.schema.json"


def load_schema():
    with open(AUDIT_SCHEMA_PATH) as f:
        return json.load(f)


class TestAuditSchemaV04Structure(unittest.TestCase):

    def setUp(self):
        self.schema = load_schema()

    # ------------------------------------------------------------------ #
    # 1. findings[].id enum includes F9-F12                               #
    # ------------------------------------------------------------------ #

    def test_finding_id_enum_includes_F9(self):
        finding_id_schema = (
            self.schema["properties"]["findings"]["items"]["properties"]["id"]
        )
        enum_vals = finding_id_schema.get("enum", [])
        self.assertIn("F9", enum_vals, "F9 not found in findings[].id enum")

    def test_finding_id_enum_includes_F10(self):
        finding_id_schema = (
            self.schema["properties"]["findings"]["items"]["properties"]["id"]
        )
        self.assertIn("F10", finding_id_schema.get("enum", []))

    def test_finding_id_enum_includes_F11(self):
        finding_id_schema = (
            self.schema["properties"]["findings"]["items"]["properties"]["id"]
        )
        self.assertIn("F11", finding_id_schema.get("enum", []))

    def test_finding_id_enum_includes_F12(self):
        finding_id_schema = (
            self.schema["properties"]["findings"]["items"]["properties"]["id"]
        )
        self.assertIn("F12", finding_id_schema.get("enum", []))

    # ------------------------------------------------------------------ #
    # 2. findings[].handoffHint optional string                           #
    # ------------------------------------------------------------------ #

    def test_finding_handoffHint_field_exists(self):
        finding_props = self.schema["properties"]["findings"]["items"]["properties"]
        self.assertIn("handoffHint", finding_props, "handoffHint field missing from findings items")
        self.assertEqual(finding_props["handoffHint"]["type"], "string")

    def test_finding_handoffHint_is_not_required(self):
        required = self.schema["properties"]["findings"]["items"].get("required", [])
        self.assertNotIn("handoffHint", required, "handoffHint should be optional, not required")

    # ------------------------------------------------------------------ #
    # 3. auditGrade.perPrompt.dimensions.injectionResistance              #
    # ------------------------------------------------------------------ #

    def _get_per_prompt_dimensions(self):
        return (
            self.schema["properties"]["auditGrade"]["properties"]["perPrompt"]
            ["additionalProperties"]["properties"]["dimensions"]["properties"]
        )

    def test_injectionResistance_dimension_exists(self):
        dims = self._get_per_prompt_dimensions()
        self.assertIn("injectionResistance", dims, "injectionResistance dimension missing")

    def test_injectionResistance_has_value_property(self):
        dims = self._get_per_prompt_dimensions()
        ir = dims["injectionResistance"]
        self.assertIn("value", ir.get("properties", {}), "injectionResistance.value missing")

    def test_injectionResistance_value_range_1_to_10(self):
        dims = self._get_per_prompt_dimensions()
        ir_value = dims["injectionResistance"]["properties"]["value"]
        self.assertEqual(ir_value.get("minimum"), 1)
        self.assertEqual(ir_value.get("maximum"), 10)

    def test_injectionResistance_has_rationale_property(self):
        dims = self._get_per_prompt_dimensions()
        ir = dims["injectionResistance"]
        self.assertIn("rationale", ir.get("properties", {}), "injectionResistance.rationale missing")

    def test_injectionResistance_rationale_is_string(self):
        dims = self._get_per_prompt_dimensions()
        ir_rationale = dims["injectionResistance"]["properties"]["rationale"]
        self.assertEqual(ir_rationale["type"], "string")

    # ------------------------------------------------------------------ #
    # 4. suggestedWeightOverrides items: rationale + appTypeSignal        #
    # ------------------------------------------------------------------ #

    def _get_suggested_weight_override_item_props(self):
        return (
            self.schema["properties"]["auditGrade"]["properties"]
            ["suggestedWeightOverrides"]["items"]["properties"]
        )

    def test_suggestedWeightOverrides_array_exists(self):
        audit_grade_props = self.schema["properties"]["auditGrade"]["properties"]
        self.assertIn(
            "suggestedWeightOverrides", audit_grade_props,
            "suggestedWeightOverrides missing from auditGrade"
        )

    def test_suggestedWeightOverrides_item_rationale_exists(self):
        props = self._get_suggested_weight_override_item_props()
        self.assertIn("rationale", props, "rationale field missing from suggestedWeightOverrides item")
        self.assertEqual(props["rationale"]["type"], "string")

    def test_suggestedWeightOverrides_item_appTypeSignal_exists(self):
        props = self._get_suggested_weight_override_item_props()
        self.assertIn("appTypeSignal", props, "appTypeSignal missing from suggestedWeightOverrides item")

    def test_suggestedWeightOverrides_appTypeSignal_enum(self):
        props = self._get_suggested_weight_override_item_props()
        enum_vals = props["appTypeSignal"].get("enum", [])
        self.assertIn("consumer", enum_vals)
        self.assertIn("internal", enum_vals)
        self.assertIn("mixed", enum_vals)

    # ------------------------------------------------------------------ #
    # 5. Backwards compat: v0.3-style audit doc still validates           #
    # ------------------------------------------------------------------ #

    def test_v03_audit_doc_still_validates(self):
        v03_doc = {
            "version": "0.1",
            "auditedAt": "2026-05-29T10:00:00Z",
            "inventoryRef": "inventory.json",
            "findings": [
                {
                    "id": "F1",
                    "smell": "Missing output schema",
                    "severity": "high",
                    "evidence": [{"file": "prompt.ts", "line": 10}],
                    "recommendation": "Add OUTPUT_SCHEMA"
                }
            ],
            "summary": {
                "totalFindings": 1,
                "byCategory": {"high": 1}
            }
        }
        try:
            validate(instance=v03_doc, schema=self.schema)
        except ValidationError as e:
            self.fail(f"v0.3 audit doc failed v0.4 schema validation: {e.message}")

    def test_v04_finding_with_handoffHint_validates(self):
        """A finding with the new handoffHint field validates."""
        doc = {
            "version": "0.1",
            "auditedAt": "2026-05-29T10:00:00Z",
            "inventoryRef": "inventory.json",
            "findings": [
                {
                    "id": "F10",
                    "smell": "User-input var without sanitization",
                    "severity": "high",
                    "evidence": [{"file": "prompt.ts", "line": 5}],
                    "recommendation": "Add sanitization directive",
                    "handoffHint": "vibe-sec:audit"
                }
            ],
            "summary": {"totalFindings": 1, "byCategory": {"high": 1}}
        }
        try:
            validate(instance=doc, schema=self.schema)
        except ValidationError as e:
            self.fail(f"v0.4 finding with handoffHint failed validation: {e.message}")

    def test_invalid_finding_id_rejected(self):
        """Unknown finding IDs (e.g. F99) should fail validation."""
        doc = {
            "version": "0.1",
            "auditedAt": "2026-05-29T10:00:00Z",
            "inventoryRef": "inventory.json",
            "findings": [
                {
                    "id": "F99",
                    "smell": "Unknown",
                    "severity": "low",
                    "evidence": [{"file": "x.ts", "line": 1}],
                    "recommendation": "Fix it"
                }
            ],
            "summary": {"totalFindings": 1, "byCategory": {"low": 1}}
        }
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
