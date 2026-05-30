"""
Task 1 (v0.6) — TDD tests for composer.schema.json v0.6 extensions.

Asserts:
  1. layers[].apiParameter enum (systemInstruction | contents | messages | instructions | prompt | null), optional
  2. layers[].apiParameterConfidence number 0-1, optional
  3. Layer type enum extended to include `global-directive`
  4. `directive-field` (v0.5 deprecated alias) STILL validates
  5. Backward compat: v0.5 composer.json validates against v0.6 schema
"""

import json
import pathlib
import unittest

from jsonschema import validate, ValidationError

SCHEMAS_DIR = pathlib.Path(__file__).parent.parent.parent / "schemas"
COMPOSER_SCHEMA_PATH = SCHEMAS_DIR / "composer.schema.json"


def load_schema():
    with open(COMPOSER_SCHEMA_PATH) as f:
        return json.load(f)


def _minimal_composer(extra_layer_props=None, top_level_extra=None, layer_type="literal"):
    layer = {"id": "L0", "type": layer_type, "text": "You are X."}
    if extra_layer_props:
        layer.update(extra_layer_props)
    doc = {
        "version": "0.1",
        "kind": "stacked",
        "layers": [layer],
    }
    if top_level_extra:
        doc.update(top_level_extra)
    return doc


class TestComposerV06ApiParameter(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_apiParameter_field_exists(self):
        layer_props = self.schema["properties"]["layers"]["items"]["properties"]
        self.assertIn("apiParameter", layer_props)

    def test_apiParameter_enum_includes_all_values(self):
        layer_props = self.schema["properties"]["layers"]["items"]["properties"]
        enum_vals = layer_props["apiParameter"]["enum"]
        for expected in [
            "systemInstruction",
            "contents",
            "messages",
            "instructions",
            "prompt",
            None,
        ]:
            self.assertIn(expected, enum_vals)

    def test_apiParameter_is_optional(self):
        required = self.schema["properties"]["layers"]["items"].get("required", [])
        self.assertNotIn("apiParameter", required)

    def test_layer_with_apiParameter_systemInstruction_validates(self):
        doc = _minimal_composer(
            extra_layer_props={"apiParameter": "systemInstruction"}
        )
        validate(instance=doc, schema=self.schema)

    def test_layer_with_apiParameter_contents_validates(self):
        doc = _minimal_composer(extra_layer_props={"apiParameter": "contents"})
        validate(instance=doc, schema=self.schema)

    def test_layer_with_apiParameter_messages_validates(self):
        doc = _minimal_composer(extra_layer_props={"apiParameter": "messages"})
        validate(instance=doc, schema=self.schema)

    def test_layer_with_apiParameter_instructions_validates(self):
        doc = _minimal_composer(extra_layer_props={"apiParameter": "instructions"})
        validate(instance=doc, schema=self.schema)

    def test_layer_with_apiParameter_prompt_validates(self):
        doc = _minimal_composer(extra_layer_props={"apiParameter": "prompt"})
        validate(instance=doc, schema=self.schema)

    def test_layer_with_apiParameter_null_validates(self):
        doc = _minimal_composer(extra_layer_props={"apiParameter": None})
        validate(instance=doc, schema=self.schema)

    def test_layer_with_invalid_apiParameter_rejected(self):
        doc = _minimal_composer(extra_layer_props={"apiParameter": "telepathy"})
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)


class TestComposerV06ApiParameterConfidence(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_apiParameterConfidence_field_exists(self):
        layer_props = self.schema["properties"]["layers"]["items"]["properties"]
        self.assertIn("apiParameterConfidence", layer_props)

    def test_apiParameterConfidence_is_number_with_range(self):
        layer_props = self.schema["properties"]["layers"]["items"]["properties"]
        apc = layer_props["apiParameterConfidence"]
        self.assertEqual(apc["type"], "number")
        self.assertEqual(apc["minimum"], 0)
        self.assertEqual(apc["maximum"], 1)

    def test_apiParameterConfidence_is_optional(self):
        required = self.schema["properties"]["layers"]["items"].get("required", [])
        self.assertNotIn("apiParameterConfidence", required)

    def test_layer_with_apiParameterConfidence_validates(self):
        doc = _minimal_composer(
            extra_layer_props={
                "apiParameter": "systemInstruction",
                "apiParameterConfidence": 0.92,
            }
        )
        validate(instance=doc, schema=self.schema)

    def test_apiParameterConfidence_above_1_rejected(self):
        doc = _minimal_composer(
            extra_layer_props={"apiParameterConfidence": 1.5}
        )
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)

    def test_apiParameterConfidence_below_0_rejected(self):
        doc = _minimal_composer(
            extra_layer_props={"apiParameterConfidence": -0.1}
        )
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)


class TestComposerV06GlobalDirectiveEnum(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_global_directive_in_type_enum(self):
        layer_props = self.schema["properties"]["layers"]["items"]["properties"]
        enum_vals = layer_props["type"]["enum"]
        self.assertIn("global-directive", enum_vals)

    def test_directive_field_still_in_type_enum_deprecated_alias(self):
        # deprecated alias preserved for backward compat
        layer_props = self.schema["properties"]["layers"]["items"]["properties"]
        enum_vals = layer_props["type"]["enum"]
        self.assertIn("directive-field", enum_vals)

    def test_layer_with_type_global_directive_validates(self):
        doc = _minimal_composer(layer_type="global-directive")
        validate(instance=doc, schema=self.schema)

    def test_layer_with_type_directive_field_still_validates(self):
        doc = _minimal_composer(layer_type="directive-field")
        validate(instance=doc, schema=self.schema)

    def test_existing_enum_values_preserved(self):
        layer_props = self.schema["properties"]["layers"]["items"]["properties"]
        enum_vals = layer_props["type"]["enum"]
        for expected in [
            "literal",
            "directive-field",
            "knowledge-injection",
            "task-instruction",
            "conditional",
        ]:
            self.assertIn(expected, enum_vals)


class TestComposerV06BackwardCompat(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_v05_minimal_composer_still_validates(self):
        doc = {
            "version": "0.1",
            "kind": "stacked",
            "layers": [
                {"id": "L0", "type": "literal", "text": "You are X."},
                {"id": "L1", "type": "directive-field", "text": "Be concise."},
            ],
        }
        validate(instance=doc, schema=self.schema)

    def test_v05_full_composer_with_confidence_fields_validates(self):
        doc = {
            "version": "0.1",
            "kind": "stacked",
            "globalConfidence": 0.85,
            "regenerationSource": "auto-detected",
            "layers": [
                {
                    "id": "L0",
                    "type": "literal",
                    "text": "You are X.",
                    "confidence": 0.95,
                },
                {
                    "id": "L1",
                    "type": "directive-field",
                    "text": "directive",
                    "confidence": 0.80,
                },
            ],
        }
        validate(instance=doc, schema=self.schema)

    def test_v06_full_composer_validates(self):
        doc = {
            "version": "0.1",
            "kind": "stacked",
            "globalConfidence": 0.88,
            "regenerationSource": "auto-detected",
            "layers": [
                {
                    "id": "L0",
                    "type": "global-directive",
                    "text": "System persona.",
                    "confidence": 0.95,
                    "apiParameter": "systemInstruction",
                    "apiParameterConfidence": 0.92,
                },
                {
                    "id": "L1",
                    "type": "knowledge-injection",
                    "text": "{{userDream}}",
                    "confidence": 0.80,
                    "apiParameter": "contents",
                    "apiParameterConfidence": 0.88,
                },
            ],
        }
        validate(instance=doc, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
