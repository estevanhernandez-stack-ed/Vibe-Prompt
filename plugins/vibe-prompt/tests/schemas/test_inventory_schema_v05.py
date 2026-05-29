"""
Task 1 — TDD tests for inventory.schema.json v0.5 extensions.

Asserts:
  1. templatedVars[] items can be string (v0.4 backward compat) OR object
  2. Object form requires `name`, supports `source` enum, `declaredAt`, `origin` enum, `originConfidence`
  3. source enum: handlebars | template-literal | concat | jsx-attr
  4. origin enum: user-controlled | system-injected | unknown
  5. originConfidence: number 0-1
  6. Backward compat: v0.4 inventory.json (string templatedVars) still validates
  7. Both registry entries AND inlinePrompts accept the new templatedVars shape
"""

import json
import pathlib
import unittest

from jsonschema import validate, ValidationError

SCHEMAS_DIR = pathlib.Path(__file__).parent.parent.parent / "schemas"
INVENTORY_SCHEMA_PATH = SCHEMAS_DIR / "inventory.schema.json"


def load_schema():
    with open(INVENTORY_SCHEMA_PATH) as f:
        return json.load(f)


def _minimal_inventory(inline_vars, registry_vars=None):
    """Build a minimal inventory doc with the given templatedVars list on one inline prompt."""
    doc = {
        "version": "0.1",
        "scannedAt": "2026-05-30T09:00:00Z",
        "targetApp": {"name": "test-app", "stack": ["typescript"], "aiProviders": ["gemini"]},
        "registry": {
            "detected": True,
            "location": "src/prompts.ts",
            "format": "ts-object",
            "entries": [
                {
                    "id": "natal_interpretation",
                    "name": "Natal Interpretation",
                    "category": "interpretation",
                    "version": "3.5.0",
                    "outputShape": "json-object",
                    "templatedVars": registry_vars if registry_vars is not None else [],
                    "voiceBearing": True,
                }
            ],
        },
        "inlinePrompts": [
            {
                "file": "src/Oneirocriton.tsx",
                "startLine": 60,
                "endLine": 100,
                "outputShape": "prose",
                "templatedVars": inline_vars,
                "voiceBearing": True,
            }
        ],
        "personas": ["Oneirocriton"],
        "modelIdentifiers": [],
    }
    return doc


class TestInventoryV05ObjectFormVars(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_inline_var_object_with_name_only_validates(self):
        doc = _minimal_inventory([{"name": "dreamText"}])
        validate(instance=doc, schema=self.schema)

    def test_inline_var_object_full_shape_validates(self):
        doc = _minimal_inventory(
            [
                {
                    "name": "dreamText",
                    "source": "template-literal",
                    "declaredAt": "src/Oneirocriton.tsx:L72",
                    "origin": "user-controlled",
                    "originConfidence": 0.92,
                }
            ]
        )
        validate(instance=doc, schema=self.schema)

    def test_inline_var_object_source_enum_handlebars(self):
        doc = _minimal_inventory([{"name": "name", "source": "handlebars"}])
        validate(instance=doc, schema=self.schema)

    def test_inline_var_object_source_enum_concat(self):
        doc = _minimal_inventory([{"name": "userMessage", "source": "concat"}])
        validate(instance=doc, schema=self.schema)

    def test_inline_var_object_source_enum_jsx_attr(self):
        doc = _minimal_inventory([{"name": "persona", "source": "jsx-attr"}])
        validate(instance=doc, schema=self.schema)

    def test_inline_var_object_invalid_source_rejected(self):
        doc = _minimal_inventory([{"name": "x", "source": "telepathy"}])
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)

    def test_inline_var_object_origin_enum_user_controlled(self):
        doc = _minimal_inventory([{"name": "dreamText", "origin": "user-controlled"}])
        validate(instance=doc, schema=self.schema)

    def test_inline_var_object_origin_enum_system_injected(self):
        doc = _minimal_inventory(
            [{"name": "knowledgeContext", "origin": "system-injected"}]
        )
        validate(instance=doc, schema=self.schema)

    def test_inline_var_object_origin_enum_unknown(self):
        doc = _minimal_inventory([{"name": "prompt", "origin": "unknown"}])
        validate(instance=doc, schema=self.schema)

    def test_inline_var_object_invalid_origin_rejected(self):
        doc = _minimal_inventory([{"name": "x", "origin": "alien"}])
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)

    def test_inline_var_object_originConfidence_in_range(self):
        for c in [0.0, 0.5, 1.0]:
            doc = _minimal_inventory(
                [{"name": "x", "originConfidence": c}]
            )
            validate(instance=doc, schema=self.schema)

    def test_inline_var_object_originConfidence_above_1_rejected(self):
        doc = _minimal_inventory([{"name": "x", "originConfidence": 1.5}])
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)

    def test_inline_var_object_originConfidence_below_0_rejected(self):
        doc = _minimal_inventory([{"name": "x", "originConfidence": -0.1}])
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)

    def test_inline_var_object_missing_name_rejected(self):
        doc = _minimal_inventory([{"source": "handlebars"}])
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)


class TestInventoryV05BackwardCompat(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_v04_string_only_inline_vars_still_validate(self):
        doc = _minimal_inventory(["name", "dob", "knowledgeContext"])
        validate(instance=doc, schema=self.schema)

    def test_v04_string_only_registry_vars_still_validate(self):
        doc = _minimal_inventory([], registry_vars=["name", "context"])
        validate(instance=doc, schema=self.schema)

    def test_mixed_string_and_object_vars_validate(self):
        doc = _minimal_inventory(
            [
                "name",
                {"name": "dreamText", "source": "template-literal"},
                "dob",
            ]
        )
        validate(instance=doc, schema=self.schema)


class TestInventoryV05RegistryEntries(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_registry_entry_object_form_var_validates(self):
        doc = _minimal_inventory(
            [],
            registry_vars=[
                {
                    "name": "name",
                    "source": "handlebars",
                    "origin": "user-controlled",
                    "originConfidence": 0.95,
                }
            ],
        )
        validate(instance=doc, schema=self.schema)

    def test_registry_invalid_source_rejected(self):
        doc = _minimal_inventory(
            [], registry_vars=[{"name": "x", "source": "nope"}]
        )
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
