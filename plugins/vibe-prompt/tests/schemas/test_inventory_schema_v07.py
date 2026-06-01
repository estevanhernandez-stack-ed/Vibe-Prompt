"""
Task 2 (v0.7) — TDD tests for inventory.schema.json v0.7 extensions.

Asserts:
  1. registry.kind enum (prompt-content | model-routing | task-mapping | hybrid),
     optional
  2. Top-level workspaces[] optional array with {name, path, packageJsonPath,
     inventoryFile} entries
  3. Top-level scanExcludes[] optional string array
  4. Top-level workspaceKind enum (single-workspace | npm-workspaces |
     nested-projects | unknown)
  5. Backward compat: v0.6 inventory.json without these fields validates
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


def _minimal_inventory(extra_top=None, registry_extra=None):
    registry = {"detected": False, "entries": []}
    if registry_extra:
        registry.update(registry_extra)
    doc = {
        "version": "0.1",
        "scannedAt": "2026-06-01T00:00:00Z",
        "targetApp": {"name": "x", "stack": [], "aiProviders": []},
        "registry": registry,
        "inlinePrompts": [],
        "personas": [],
        "modelIdentifiers": [],
    }
    if extra_top:
        doc.update(extra_top)
    return doc


class TestInventoryV07RegistryKind(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_registry_kind_field_declared(self):
        registry_props = self.schema["properties"]["registry"]["properties"]
        self.assertIn("kind", registry_props)

    def test_registry_kind_enum_values(self):
        registry_props = self.schema["properties"]["registry"]["properties"]
        kind_enum = registry_props["kind"]["enum"]
        for expected in [
            "prompt-content",
            "model-routing",
            "task-mapping",
            "hybrid",
        ]:
            self.assertIn(expected, kind_enum)

    def test_registry_kind_is_optional(self):
        required = self.schema["properties"]["registry"].get("required", [])
        self.assertNotIn("kind", required)

    def test_inventory_with_registry_kind_prompt_content_validates(self):
        doc = _minimal_inventory(registry_extra={"kind": "prompt-content"})
        validate(instance=doc, schema=self.schema)

    def test_inventory_with_registry_kind_model_routing_validates(self):
        doc = _minimal_inventory(registry_extra={"kind": "model-routing"})
        validate(instance=doc, schema=self.schema)

    def test_inventory_with_registry_kind_task_mapping_validates(self):
        doc = _minimal_inventory(registry_extra={"kind": "task-mapping"})
        validate(instance=doc, schema=self.schema)

    def test_inventory_with_registry_kind_hybrid_validates(self):
        doc = _minimal_inventory(registry_extra={"kind": "hybrid"})
        validate(instance=doc, schema=self.schema)

    def test_inventory_with_invalid_registry_kind_rejected(self):
        doc = _minimal_inventory(registry_extra={"kind": "telepathy"})
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)


class TestInventoryV07Workspaces(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_workspaces_field_declared(self):
        self.assertIn("workspaces", self.schema["properties"])

    def test_workspaces_is_array(self):
        ws = self.schema["properties"]["workspaces"]
        self.assertEqual(ws["type"], "array")

    def test_workspaces_is_optional(self):
        required = self.schema.get("required", [])
        self.assertNotIn("workspaces", required)

    def test_workspaces_item_required_fields(self):
        item = self.schema["properties"]["workspaces"]["items"]
        for expected in ["name", "path", "packageJsonPath", "inventoryFile"]:
            self.assertIn(expected, item["properties"])

    def test_inventory_with_workspaces_validates(self):
        doc = _minimal_inventory(
            extra_top={
                "workspaces": [
                    {
                        "name": "cinema",
                        "path": "apps/cinema",
                        "packageJsonPath": "apps/cinema/package.json",
                        "inventoryFile": ".vibe-prompt/state/inventory-cinema.json",
                    }
                ]
            }
        )
        validate(instance=doc, schema=self.schema)


class TestInventoryV07ScanExcludes(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_scanExcludes_field_declared(self):
        self.assertIn("scanExcludes", self.schema["properties"])

    def test_scanExcludes_is_optional(self):
        required = self.schema.get("required", [])
        self.assertNotIn("scanExcludes", required)

    def test_scanExcludes_is_string_array(self):
        se = self.schema["properties"]["scanExcludes"]
        self.assertEqual(se["type"], "array")
        self.assertEqual(se["items"]["type"], "string")

    def test_inventory_with_scanExcludes_validates(self):
        doc = _minimal_inventory(
            extra_top={
                "scanExcludes": [
                    "vibe-*/",
                    "_ARCHIVE_*/",
                    "node_modules/",
                ]
            }
        )
        validate(instance=doc, schema=self.schema)


class TestInventoryV07WorkspaceKind(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_workspaceKind_field_declared(self):
        self.assertIn("workspaceKind", self.schema["properties"])

    def test_workspaceKind_enum(self):
        wk = self.schema["properties"]["workspaceKind"]
        for expected in [
            "single-workspace",
            "npm-workspaces",
            "nested-projects",
            "unknown",
        ]:
            self.assertIn(expected, wk["enum"])

    def test_workspaceKind_is_optional(self):
        required = self.schema.get("required", [])
        self.assertNotIn("workspaceKind", required)

    def test_inventory_with_workspaceKind_npm_workspaces_validates(self):
        doc = _minimal_inventory(extra_top={"workspaceKind": "npm-workspaces"})
        validate(instance=doc, schema=self.schema)

    def test_inventory_with_invalid_workspaceKind_rejected(self):
        doc = _minimal_inventory(extra_top={"workspaceKind": "polyrepo"})
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)


class TestInventoryV07BackwardCompat(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_v06_inventory_validates(self):
        doc = {
            "version": "0.1",
            "scannedAt": "2026-05-29T00:00:00Z",
            "targetApp": {
                "name": "celestia3",
                "stack": ["typescript", "vite"],
                "aiProviders": ["gemini"],
            },
            "registry": {
                "detected": True,
                "location": "src/prompts/registry.ts",
                "format": "typescript-module",
                "entries": [
                    {
                        "id": "natalReading",
                        "category": "reading",
                        "version": "1.0",
                        "outputShape": "prose",
                        "voiceBearing": True,
                    }
                ],
            },
            "inlinePrompts": [],
            "personas": ["pilgrim"],
            "modelIdentifiers": [
                {
                    "value": "gemini-2.5-flash",
                    "occurrences": [{"file": "src/lib/gemini.ts", "line": 12}],
                }
            ],
        }
        validate(instance=doc, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
