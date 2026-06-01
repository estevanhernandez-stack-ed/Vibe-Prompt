"""
Task 1 (v0.7) — TDD tests for composer.schema.json v0.7 extensions.

Asserts:
  1. Top-level `composers[]` array (each entry: kind, path, layers[],
     globalConfidence, regenerationSource, apiParameterCompleteness)
  2. `kind` enum on each composer entry:
     single-composer | multi-composer | multi-call-site | shared-package
  3. Top-level `compositionShape` enum (single | multi)
  4. Backward compat: v0.6 composer.json (top-level `layers[]`, no
     `composers[]`) validates
  5. v0.5 composer.json with `directive-field` layer type still validates
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


class TestComposerV07ComposersArray(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_composers_field_declared(self):
        self.assertIn("composers", self.schema["properties"])

    def test_composers_is_array(self):
        composers = self.schema["properties"]["composers"]
        self.assertEqual(composers["type"], "array")

    def test_composers_item_has_kind_property(self):
        item = self.schema["properties"]["composers"]["items"]
        self.assertIn("kind", item["properties"])

    def test_composers_item_kind_enum(self):
        item = self.schema["properties"]["composers"]["items"]
        kind_enum = item["properties"]["kind"]["enum"]
        for expected in [
            "single-composer",
            "multi-composer",
            "multi-call-site",
            "shared-package",
        ]:
            self.assertIn(expected, kind_enum)

    def test_composers_item_has_path(self):
        item = self.schema["properties"]["composers"]["items"]
        self.assertIn("path", item["properties"])

    def test_composers_item_has_layers(self):
        item = self.schema["properties"]["composers"]["items"]
        self.assertIn("layers", item["properties"])

    def test_composers_item_has_globalConfidence(self):
        item = self.schema["properties"]["composers"]["items"]
        self.assertIn("globalConfidence", item["properties"])

    def test_composers_item_has_regenerationSource(self):
        item = self.schema["properties"]["composers"]["items"]
        self.assertIn("regenerationSource", item["properties"])

    def test_composers_item_has_apiParameterCompleteness(self):
        item = self.schema["properties"]["composers"]["items"]
        self.assertIn("apiParameterCompleteness", item["properties"])

    def test_v07_multi_composer_doc_validates(self):
        doc = {
            "version": "0.1",
            "kind": "stacked",
            "compositionShape": "multi",
            "composers": [
                {
                    "kind": "multi-composer",
                    "path": "src/galaxyCore.ts",
                    "globalConfidence": 0.88,
                    "regenerationSource": "auto-detected",
                    "apiParameterCompleteness": 1.0,
                    "layers": [
                        {
                            "id": "L0",
                            "type": "global-directive",
                            "text": "You are the Galaxy Core.",
                            "apiParameter": "systemInstruction",
                            "apiParameterConfidence": 0.9,
                        }
                    ],
                },
                {
                    "kind": "multi-composer",
                    "path": "src/ChatController.ts",
                    "globalConfidence": 0.82,
                    "regenerationSource": "auto-detected",
                    "apiParameterCompleteness": 0.5,
                    "layers": [
                        {
                            "id": "L0",
                            "type": "literal",
                            "text": "Chat persona.",
                        }
                    ],
                },
            ],
        }
        validate(instance=doc, schema=self.schema)

    def test_multi_call_site_composer_path_can_be_array(self):
        # For multi-call-site, path may be an array of call sites.
        # Schema must accept either string or array of strings.
        doc = {
            "version": "0.1",
            "kind": "stacked",
            "compositionShape": "multi",
            "composers": [
                {
                    "kind": "multi-call-site",
                    "path": ["src/a.ts", "src/b.ts", "src/c.ts"],
                    "globalConfidence": 0.7,
                    "regenerationSource": "auto-detected",
                    "apiParameterCompleteness": 0.0,
                    "layers": [
                        {
                            "id": "L0",
                            "type": "literal",
                            "text": "Inline persona.",
                        }
                    ],
                }
            ],
        }
        validate(instance=doc, schema=self.schema)


class TestComposerV07CompositionShape(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_compositionShape_field_declared(self):
        self.assertIn("compositionShape", self.schema["properties"])

    def test_compositionShape_enum_has_single_and_multi(self):
        shape = self.schema["properties"]["compositionShape"]
        self.assertIn("single", shape["enum"])
        self.assertIn("multi", shape["enum"])

    def test_compositionShape_is_optional(self):
        required = self.schema.get("required", [])
        self.assertNotIn("compositionShape", required)

    def test_invalid_compositionShape_rejected(self):
        doc = {
            "version": "0.1",
            "kind": "stacked",
            "compositionShape": "telepathic",
            "layers": [
                {"id": "L0", "type": "literal", "text": "X."}
            ],
        }
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)


class TestComposerV07BackwardCompat(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_v06_top_level_layers_still_validates(self):
        # v0.6 single-composer shape (no composers[]); top-level layers[] only
        doc = {
            "version": "0.1",
            "kind": "stacked",
            "globalConfidence": 0.88,
            "regenerationSource": "auto-detected",
            "layers": [
                {
                    "id": "L0",
                    "type": "global-directive",
                    "text": "Persona.",
                    "apiParameter": "systemInstruction",
                    "apiParameterConfidence": 0.92,
                }
            ],
        }
        validate(instance=doc, schema=self.schema)

    def test_v05_directive_field_still_validates(self):
        doc = {
            "version": "0.1",
            "kind": "stacked",
            "layers": [
                {"id": "L0", "type": "literal", "text": "X."},
                {"id": "L1", "type": "directive-field", "text": "Be concise."},
            ],
        }
        validate(instance=doc, schema=self.schema)

    def test_v06_full_composer_validates(self):
        doc = {
            "version": "0.1",
            "kind": "stacked",
            "globalConfidence": 0.85,
            "regenerationSource": "auto-detected",
            "layers": [
                {
                    "id": "L0",
                    "type": "literal",
                    "text": "X.",
                    "confidence": 0.9,
                    "apiParameter": "systemInstruction",
                    "apiParameterConfidence": 0.9,
                }
            ],
        }
        validate(instance=doc, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
