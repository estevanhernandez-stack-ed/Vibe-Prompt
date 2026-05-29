"""
Task 3 — TDD tests for grade-result.schema.json + baseline.schema.json v0.4 extensions.

grade-result:
  - perPrompt[*].composite.dimensions.injectionResistance exists
  - perPrompt[*].composite.weights.injectionResistance exists (number)
  - appComposite.dimensions.injectionResistance exists (spec says appComposite is extended likewise)

baseline:
  - perPromptBaseline[*].bestScores.injectionResistance with {best: number, achievedAt: ISO-string}

Backwards compat: v0.3 docs still validate.
"""

import json
import pathlib
import unittest

import jsonschema
from jsonschema import validate, ValidationError

SCHEMAS_DIR = pathlib.Path(__file__).parent.parent.parent / "schemas"
GRADE_SCHEMA_PATH = SCHEMAS_DIR / "grade-result.schema.json"
BASELINE_SCHEMA_PATH = SCHEMAS_DIR / "baseline.schema.json"


def load_grade_schema():
    with open(GRADE_SCHEMA_PATH) as f:
        return json.load(f)


def load_baseline_schema():
    with open(BASELINE_SCHEMA_PATH) as f:
        return json.load(f)


class TestGradeResultSchemaV04(unittest.TestCase):

    def setUp(self):
        self.schema = load_grade_schema()

    def _per_prompt_props(self):
        return (
            self.schema["properties"]["perPrompt"]
            ["additionalProperties"]["properties"]
        )

    # ------------------------------------------------------------------ #
    # perPrompt[*].dimensions.injectionResistance                         #
    # ------------------------------------------------------------------ #

    def test_perPrompt_dimensions_injectionResistance_exists(self):
        dims = self._per_prompt_props()["dimensions"]["properties"]
        self.assertIn("injectionResistance", dims)

    def test_perPrompt_dimensions_injectionResistance_range(self):
        dims = self._per_prompt_props()["dimensions"]["properties"]
        ir = dims["injectionResistance"]
        self.assertEqual(ir.get("minimum"), 1)
        self.assertEqual(ir.get("maximum"), 10)

    # ------------------------------------------------------------------ #
    # perPrompt[*].weights.injectionResistance                            #
    # ------------------------------------------------------------------ #

    def test_perPrompt_weights_field_exists(self):
        props = self._per_prompt_props()
        self.assertIn("weights", props, "weights field missing from perPrompt items")

    def test_perPrompt_weights_injectionResistance_exists(self):
        props = self._per_prompt_props()
        weight_props = props["weights"]["properties"]
        self.assertIn("injectionResistance", weight_props)

    def test_perPrompt_weights_injectionResistance_is_number(self):
        props = self._per_prompt_props()
        ir_weight = props["weights"]["properties"]["injectionResistance"]
        self.assertEqual(ir_weight["type"], "number")

    # ------------------------------------------------------------------ #
    # appComposite extended (spec says "likewise")                        #
    # ------------------------------------------------------------------ #

    def test_appComposite_dimensions_field_exists(self):
        """appComposite should be extended to an object with dimensions."""
        top = self.schema["properties"]
        # v0.3 had appComposite as a plain integer; v0.4 extends it.
        # The schema may keep backward compat via oneOf or an object type.
        ac = top["appComposite"]
        # Accept either an object-with-dimensions or a schema that allows both.
        is_object = ac.get("type") == "object"
        has_one_of = "oneOf" in ac or "anyOf" in ac
        self.assertTrue(
            is_object or has_one_of,
            "appComposite should be extended to an object type (or oneOf) with dimensions"
        )

    def test_appComposite_dimensions_injectionResistance_accessible(self):
        top = self.schema["properties"]
        ac = top["appComposite"]
        # Navigate to properties depending on schema shape
        if ac.get("type") == "object":
            dims = ac.get("properties", {}).get("dimensions", {}).get("properties", {})
        elif "oneOf" in ac:
            # Find the object variant
            obj_variant = next((s for s in ac["oneOf"] if s.get("type") == "object"), None)
            self.assertIsNotNone(obj_variant, "No object variant in appComposite oneOf")
            dims = obj_variant.get("properties", {}).get("dimensions", {}).get("properties", {})
        else:
            self.fail("Cannot navigate appComposite to dimensions")
        self.assertIn("injectionResistance", dims)

    # ------------------------------------------------------------------ #
    # Backwards compat                                                    #
    # ------------------------------------------------------------------ #

    def test_v03_grade_result_still_validates(self):
        v03_doc = {
            "version": "0.3",
            "runId": "run-0529-0001",
            "computedAt": "2026-05-29T10:00:00Z",
            "perPrompt": {
                "natal_interpretation": {
                    "composite": 7,
                    "dimensions": {
                        "schemaTightness": 8,
                        "personaConsistency": 7,
                        "instructionClarity": 6,
                        "tokenEfficiency": 7
                    }
                }
            },
            "appComposite": 7
        }
        try:
            validate(instance=v03_doc, schema=self.schema)
        except ValidationError as e:
            self.fail(f"v0.3 grade-result failed v0.4 schema: {e.message}")

    def test_v04_grade_result_with_injectionResistance_validates(self):
        doc = {
            "version": "0.3",
            "runId": "run-0529-0002",
            "computedAt": "2026-05-29T11:00:00Z",
            "perPrompt": {
                "natal_interpretation": {
                    "composite": 6,
                    "dimensions": {
                        "schemaTightness": 8,
                        "personaConsistency": 7,
                        "instructionClarity": 6,
                        "tokenEfficiency": 7,
                        "injectionResistance": 4
                    },
                    "weights": {
                        "schemaTightness": 0.20,
                        "personaConsistency": 0.20,
                        "instructionClarity": 0.20,
                        "tokenEfficiency": 0.20,
                        "injectionResistance": 0.20
                    }
                }
            },
            "appComposite": {
                "value": 6,
                "dimensions": {
                    "schemaTightness": 8,
                    "personaConsistency": 7,
                    "instructionClarity": 6,
                    "tokenEfficiency": 7,
                    "injectionResistance": 4
                }
            }
        }
        try:
            validate(instance=doc, schema=self.schema)
        except ValidationError as e:
            self.fail(f"v0.4 grade-result with injectionResistance failed: {e.message}")


class TestBaselineSchemaV04(unittest.TestCase):

    def setUp(self):
        self.schema = load_baseline_schema()

    # ------------------------------------------------------------------ #
    # perPromptBaseline[*].bestScores.injectionResistance                 #
    # ------------------------------------------------------------------ #

    def test_perPromptBaseline_bestScores_field_exists(self):
        per_prompt_props = (
            self.schema["properties"]["perPromptBaseline"]
            ["additionalProperties"]["properties"]
        )
        self.assertIn("bestScores", per_prompt_props, "bestScores field missing from perPromptBaseline")

    def test_bestScores_injectionResistance_exists(self):
        per_prompt_props = (
            self.schema["properties"]["perPromptBaseline"]
            ["additionalProperties"]["properties"]
        )
        best_scores_props = per_prompt_props["bestScores"]["properties"]
        self.assertIn("injectionResistance", best_scores_props)

    def test_bestScores_injectionResistance_best_is_number(self):
        per_prompt_props = (
            self.schema["properties"]["perPromptBaseline"]
            ["additionalProperties"]["properties"]
        )
        ir = per_prompt_props["bestScores"]["properties"]["injectionResistance"]["properties"]
        self.assertEqual(ir["best"]["type"], "number")

    def test_bestScores_injectionResistance_achievedAt_is_string(self):
        per_prompt_props = (
            self.schema["properties"]["perPromptBaseline"]
            ["additionalProperties"]["properties"]
        )
        ir = per_prompt_props["bestScores"]["properties"]["injectionResistance"]["properties"]
        self.assertEqual(ir["achievedAt"]["type"], "string")

    # ------------------------------------------------------------------ #
    # Backwards compat                                                    #
    # ------------------------------------------------------------------ #

    def test_v03_baseline_still_validates(self):
        v03_doc = {
            "version": "0.3",
            "establishedAt": "2026-05-29T10:00:00Z",
            "lastAdvancedAt": "2026-05-29T10:00:00Z",
            "perPromptBaseline": {
                "natal_interpretation": {
                    "composite": 7,
                    "dimensions": {
                        "schemaTightness": 8,
                        "personaConsistency": 7,
                        "instructionClarity": 6,
                        "tokenEfficiency": 7
                    },
                    "establishedInRunId": "run-0529-0001"
                }
            },
            "appComposite": 7
        }
        try:
            validate(instance=v03_doc, schema=self.schema)
        except ValidationError as e:
            self.fail(f"v0.3 baseline failed v0.4 schema: {e.message}")

    def test_v04_baseline_with_bestScores_validates(self):
        doc = {
            "version": "0.3",
            "establishedAt": "2026-05-29T10:00:00Z",
            "lastAdvancedAt": "2026-05-29T10:00:00Z",
            "perPromptBaseline": {
                "natal_interpretation": {
                    "composite": 7,
                    "dimensions": {
                        "schemaTightness": 8,
                        "personaConsistency": 7,
                        "instructionClarity": 6,
                        "tokenEfficiency": 7,
                        "injectionResistance": 5
                    },
                    "establishedInRunId": "run-0529-0001",
                    "bestScores": {
                        "injectionResistance": {
                            "best": 5,
                            "achievedAt": "2026-05-29T10:00:00Z"
                        }
                    }
                }
            },
            "appComposite": 7
        }
        try:
            validate(instance=doc, schema=self.schema)
        except ValidationError as e:
            self.fail(f"v0.4 baseline with bestScores failed: {e.message}")


if __name__ == "__main__":
    unittest.main()
