"""
Task 2 — TDD tests for run-result.schema.json v0.4 extensions.

Asserts:
  1. mechanical-finding category enum includes value-type-drift + value-type-drift-both
  2. run-result accepts injectAttackResults (optional array)
  3. run-result accepts injectAttackSummary (optional object) with {successfulAttacks, resistanceRate}
  4. evalGrade.dimensions.injectionResistance exists
  5. Backwards compat: a v0.3-style run-result doc still validates
"""

import json
import pathlib
import unittest

import jsonschema
from jsonschema import validate, ValidationError

SCHEMAS_DIR = pathlib.Path(__file__).parent.parent.parent / "schemas"
SCHEMA_PATH = SCHEMAS_DIR / "run-result.schema.json"


def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


# Minimal valid v0.3 run-result document (reused across tests).
V03_DOC = {
    "version": "0.1",
    "runId": "run-0529-0001",
    "startedAt": "2026-05-29T10:00:00Z",
    "completedAt": "2026-05-29T10:05:00Z",
    "mode": "drift",
    "agentIdentity": {"name": "vibe-prompt-eval", "model": "claude-sonnet-4-6"},
    "prompts": [
        {
            "id": "natal_interpretation",
            "fixture": {"origin": "synthesized", "data": {"birthDate": "1990-01-01"}},
            "outputs": {
                "prod": {
                    "model": "gemini-2.5-flash",
                    "text": "Your natal chart...",
                    "tokens": 200,
                    "costUsd": 0.001
                }
            },
            "comparator": {
                "mechanical": [
                    {"check": "schema-shape", "severity": "medium", "fired": False}
                ],
                "llmJudge": {"skipped": False, "findings": []}
            }
        }
    ],
    "summary": {
        "totalPrompts": 1,
        "totalCostUsd": 0.001,
        "highSeverityCount": 0
    }
}


class TestRunResultSchemaV04Structure(unittest.TestCase):

    def setUp(self):
        self.schema = load_schema()

    # ------------------------------------------------------------------ #
    # 1. mechanical category enum: value-type-drift variants              #
    # ------------------------------------------------------------------ #

    def _get_mechanical_item_props(self):
        return (
            self.schema["properties"]["prompts"]["items"]
            ["properties"]["comparator"]["properties"]["mechanical"]
            ["items"]["properties"]
        )

    def test_mechanical_check_field_exists(self):
        props = self._get_mechanical_item_props()
        self.assertIn("check", props)

    def test_mechanical_category_field_exists(self):
        """Schema should have a 'category' field (or 'check' used as category)."""
        # The current schema uses 'check' as the category-ish field. v0.4 adds a
        # dedicated 'category' enum field for the comparator, per spec §2 + plan Task 2.
        props = self._get_mechanical_item_props()
        self.assertIn(
            "category", props,
            "mechanical finding should have a 'category' enum field with value-type-drift"
        )

    def test_value_type_drift_in_category_enum(self):
        props = self._get_mechanical_item_props()
        enum_vals = props["category"].get("enum", [])
        self.assertIn("value-type-drift", enum_vals)

    def test_value_type_drift_both_in_category_enum(self):
        props = self._get_mechanical_item_props()
        enum_vals = props["category"].get("enum", [])
        self.assertIn("value-type-drift-both", enum_vals)

    # ------------------------------------------------------------------ #
    # 2. injectAttackResults optional array                               #
    # ------------------------------------------------------------------ #

    def test_injectAttackResults_field_exists(self):
        self.assertIn(
            "injectAttackResults",
            self.schema["properties"],
            "injectAttackResults missing from top-level schema properties"
        )

    def test_injectAttackResults_is_array(self):
        field = self.schema["properties"]["injectAttackResults"]
        self.assertEqual(field["type"], "array")

    def test_injectAttackResults_not_required(self):
        required = self.schema.get("required", [])
        self.assertNotIn("injectAttackResults", required)

    def test_injectAttackResults_item_has_fixtureName(self):
        items = self.schema["properties"]["injectAttackResults"]["items"]
        self.assertIn("fixtureName", items.get("properties", {}))

    def test_injectAttackResults_item_has_honoredAttack(self):
        items = self.schema["properties"]["injectAttackResults"]["items"]
        self.assertIn("honoredAttack", items.get("properties", {}))

    def test_injectAttackResults_item_honoredAttack_is_bool(self):
        items = self.schema["properties"]["injectAttackResults"]["items"]
        self.assertEqual(items["properties"]["honoredAttack"]["type"], "boolean")

    # ------------------------------------------------------------------ #
    # 3. injectAttackSummary optional object                              #
    # ------------------------------------------------------------------ #

    def test_injectAttackSummary_field_exists(self):
        self.assertIn(
            "injectAttackSummary",
            self.schema["properties"],
            "injectAttackSummary missing from top-level schema properties"
        )

    def test_injectAttackSummary_not_required(self):
        required = self.schema.get("required", [])
        self.assertNotIn("injectAttackSummary", required)

    def test_injectAttackSummary_successfulAttacks_exists(self):
        summary_props = self.schema["properties"]["injectAttackSummary"]["properties"]
        self.assertIn("successfulAttacks", summary_props)
        self.assertEqual(summary_props["successfulAttacks"]["type"], "integer")

    def test_injectAttackSummary_resistanceRate_exists(self):
        summary_props = self.schema["properties"]["injectAttackSummary"]["properties"]
        self.assertIn("resistanceRate", summary_props)
        self.assertEqual(summary_props["resistanceRate"]["type"], "number")

    # ------------------------------------------------------------------ #
    # 4. evalGrade.dimensions.injectionResistance                         #
    # ------------------------------------------------------------------ #

    def _get_eval_grade_dimensions(self):
        return (
            self.schema["properties"]["prompts"]["items"]
            ["properties"]["evalGrade"]["properties"]["dimensions"]["properties"]
        )

    def test_evalGrade_injectionResistance_exists(self):
        dims = self._get_eval_grade_dimensions()
        self.assertIn("injectionResistance", dims, "evalGrade.dimensions.injectionResistance missing")

    def test_evalGrade_injectionResistance_range(self):
        dims = self._get_eval_grade_dimensions()
        ir = dims["injectionResistance"]
        self.assertEqual(ir.get("minimum"), 1)
        self.assertEqual(ir.get("maximum"), 10)

    # ------------------------------------------------------------------ #
    # 5. Backwards compat                                                 #
    # ------------------------------------------------------------------ #

    def test_v03_run_result_still_validates(self):
        try:
            validate(instance=V03_DOC, schema=self.schema)
        except ValidationError as e:
            self.fail(f"v0.3 run-result failed v0.4 schema validation: {e.message}")

    def test_v04_with_injectAttackResults_validates(self):
        doc = dict(V03_DOC)
        doc["injectAttackResults"] = [
            {
                "fixtureName": "direct-override-v1",
                "vendor": "gemini",
                "honoredAttack": False,
                "judgeReasoning": "Model maintained persona",
                "severity": "high"
            }
        ]
        doc["injectAttackSummary"] = {
            "successfulAttacks": 0,
            "resistanceRate": 1.0
        }
        try:
            validate(instance=doc, schema=self.schema)
        except ValidationError as e:
            self.fail(f"v0.4 run-result with inject-attack fields failed: {e.message}")

    def test_v04_mechanical_finding_value_type_drift_validates(self):
        """A mechanical finding with category=value-type-drift should validate."""
        doc = dict(V03_DOC)
        prompt = dict(doc["prompts"][0])
        prompt["comparator"] = {
            "mechanical": [
                {
                    "check": "value-type-drift",
                    "category": "value-type-drift",
                    "severity": "medium",
                    "fired": True,
                    "evidence": {
                        "keyPath": "bigThree",
                        "declaredType": "string",
                        "prodType": "array<object>",
                        "baselineType": "string",
                        "driftedSide": "prod",
                        "snippet": "[{\"sun\": \"Aries\"}, {\"moon\": \"Cancer\"}]"
                    }
                }
            ],
            "llmJudge": {"skipped": True}
        }
        doc["prompts"] = [prompt]
        try:
            validate(instance=doc, schema=self.schema)
        except ValidationError as e:
            self.fail(f"value-type-drift mechanical finding failed validation: {e.message}")


if __name__ == "__main__":
    unittest.main()
