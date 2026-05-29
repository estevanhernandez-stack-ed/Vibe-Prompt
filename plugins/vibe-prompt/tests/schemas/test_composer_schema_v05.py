"""
Task 2 — TDD tests for composer.schema.json v0.5 extensions.

Asserts:
  1. layers[].confidence is number 0-1
  2. Top-level globalConfidence is number 0-1
  3. Top-level regenerationSource enum: manual | auto-detected | hybrid
  4. Backward compat: v0.4 composer doc (no new fields) still validates
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


def _minimal_composer(extra_layer_props=None, top_level_extra=None):
    layer = {"id": "L0", "type": "literal", "text": "You are X."}
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


class TestComposerV05LayerConfidence(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_layer_confidence_field_exists(self):
        layer_props = self.schema["properties"]["layers"]["items"]["properties"]
        self.assertIn("confidence", layer_props)

    def test_layer_confidence_is_number(self):
        layer_props = self.schema["properties"]["layers"]["items"]["properties"]
        self.assertEqual(layer_props["confidence"]["type"], "number")

    def test_layer_confidence_range(self):
        layer_props = self.schema["properties"]["layers"]["items"]["properties"]
        self.assertEqual(layer_props["confidence"]["minimum"], 0)
        self.assertEqual(layer_props["confidence"]["maximum"], 1)

    def test_layer_with_confidence_validates(self):
        doc = _minimal_composer(extra_layer_props={"confidence": 0.92})
        validate(instance=doc, schema=self.schema)

    def test_layer_confidence_above_1_rejected(self):
        doc = _minimal_composer(extra_layer_props={"confidence": 1.5})
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)

    def test_layer_confidence_below_0_rejected(self):
        doc = _minimal_composer(extra_layer_props={"confidence": -0.1})
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)


class TestComposerV05GlobalConfidence(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_globalConfidence_field_exists(self):
        top_props = self.schema["properties"]
        self.assertIn("globalConfidence", top_props)

    def test_globalConfidence_is_number(self):
        gc = self.schema["properties"]["globalConfidence"]
        self.assertEqual(gc["type"], "number")
        self.assertEqual(gc["minimum"], 0)
        self.assertEqual(gc["maximum"], 1)

    def test_globalConfidence_value_validates(self):
        doc = _minimal_composer(top_level_extra={"globalConfidence": 0.75})
        validate(instance=doc, schema=self.schema)

    def test_globalConfidence_above_1_rejected(self):
        doc = _minimal_composer(top_level_extra={"globalConfidence": 1.1})
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)


class TestComposerV05RegenerationSource(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_regenerationSource_field_exists(self):
        top_props = self.schema["properties"]
        self.assertIn("regenerationSource", top_props)

    def test_regenerationSource_enum(self):
        enum_vals = self.schema["properties"]["regenerationSource"]["enum"]
        self.assertIn("manual", enum_vals)
        self.assertIn("auto-detected", enum_vals)
        self.assertIn("hybrid", enum_vals)

    def test_regenerationSource_manual_validates(self):
        doc = _minimal_composer(top_level_extra={"regenerationSource": "manual"})
        validate(instance=doc, schema=self.schema)

    def test_regenerationSource_auto_detected_validates(self):
        doc = _minimal_composer(
            top_level_extra={"regenerationSource": "auto-detected"}
        )
        validate(instance=doc, schema=self.schema)

    def test_regenerationSource_hybrid_validates(self):
        doc = _minimal_composer(top_level_extra={"regenerationSource": "hybrid"})
        validate(instance=doc, schema=self.schema)

    def test_regenerationSource_invalid_rejected(self):
        doc = _minimal_composer(top_level_extra={"regenerationSource": "telepathy"})
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)


class TestComposerV05BackwardCompat(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_v04_minimal_composer_still_validates(self):
        doc = {
            "version": "0.1",
            "kind": "stacked",
            "layers": [
                {"id": "L0", "type": "literal", "text": "You are X."},
                {"id": "L1", "type": "directive-field", "text": "Be concise."},
            ],
        }
        validate(instance=doc, schema=self.schema)

    def test_v05_full_composer_validates(self):
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
                    "type": "knowledge-injection",
                    "text": "knowledge",
                    "confidence": 0.80,
                },
            ],
        }
        validate(instance=doc, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
