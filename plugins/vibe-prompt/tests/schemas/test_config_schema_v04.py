"""
Task 4 — TDD tests for config.schema.json v0.4 extensions.

Asserts:
  1. eval.injectAttack.enabled (boolean, default false)
  2. eval.injectAttack.fixtures (string array)
  3. eval.injectAttack.costCeiling (number, default 0.20)
  4. audit.injectionResistance.userInputVars (string array)
  5. Backwards compat: v0.3-style config still validates
"""

import json
import pathlib
import unittest

import jsonschema
from jsonschema import validate, ValidationError

SCHEMAS_DIR = pathlib.Path(__file__).parent.parent.parent / "schemas"
CONFIG_SCHEMA_PATH = SCHEMAS_DIR / "config.schema.json"


def load_schema():
    with open(CONFIG_SCHEMA_PATH) as f:
        return json.load(f)


class TestConfigSchemaV04(unittest.TestCase):

    def setUp(self):
        self.schema = load_schema()

    # ------------------------------------------------------------------ #
    # Helper: navigate to eval.injectAttack properties                    #
    # ------------------------------------------------------------------ #

    def _get_inject_attack_props(self):
        return (
            self.schema["properties"]["eval"]
            ["properties"]["injectAttack"]["properties"]
        )

    def _get_audit_injection_resistance_props(self):
        return (
            self.schema["properties"]["audit"]
            ["properties"]["injectionResistance"]["properties"]
        )

    # ------------------------------------------------------------------ #
    # 1. eval.injectAttack.enabled                                        #
    # ------------------------------------------------------------------ #

    def test_eval_field_exists(self):
        self.assertIn("eval", self.schema["properties"], "eval field missing from config schema")

    def test_eval_injectAttack_field_exists(self):
        eval_props = self.schema["properties"]["eval"]["properties"]
        self.assertIn("injectAttack", eval_props, "eval.injectAttack missing")

    def test_eval_injectAttack_enabled_is_boolean(self):
        props = self._get_inject_attack_props()
        self.assertIn("enabled", props)
        self.assertEqual(props["enabled"]["type"], "boolean")

    def test_eval_injectAttack_enabled_default_false(self):
        props = self._get_inject_attack_props()
        self.assertEqual(props["enabled"].get("default"), False)

    # ------------------------------------------------------------------ #
    # 2. eval.injectAttack.fixtures (string array)                        #
    # ------------------------------------------------------------------ #

    def test_eval_injectAttack_fixtures_is_array(self):
        props = self._get_inject_attack_props()
        self.assertIn("fixtures", props)
        self.assertEqual(props["fixtures"]["type"], "array")

    def test_eval_injectAttack_fixtures_items_are_strings(self):
        props = self._get_inject_attack_props()
        self.assertEqual(props["fixtures"]["items"]["type"], "string")

    # ------------------------------------------------------------------ #
    # 3. eval.injectAttack.costCeiling                                    #
    # ------------------------------------------------------------------ #

    def test_eval_injectAttack_costCeiling_is_number(self):
        props = self._get_inject_attack_props()
        self.assertIn("costCeiling", props)
        self.assertEqual(props["costCeiling"]["type"], "number")

    def test_eval_injectAttack_costCeiling_default_020(self):
        props = self._get_inject_attack_props()
        self.assertAlmostEqual(props["costCeiling"].get("default"), 0.20)

    # ------------------------------------------------------------------ #
    # 4. audit.injectionResistance.userInputVars (string array)           #
    # ------------------------------------------------------------------ #

    def test_audit_field_exists(self):
        self.assertIn("audit", self.schema["properties"], "audit field missing from config schema")

    def test_audit_injectionResistance_field_exists(self):
        audit_props = self.schema["properties"]["audit"]["properties"]
        self.assertIn("injectionResistance", audit_props, "audit.injectionResistance missing")

    def test_audit_injectionResistance_userInputVars_is_array(self):
        props = self._get_audit_injection_resistance_props()
        self.assertIn("userInputVars", props)
        self.assertEqual(props["userInputVars"]["type"], "array")

    def test_audit_injectionResistance_userInputVars_items_are_strings(self):
        props = self._get_audit_injection_resistance_props()
        self.assertEqual(props["userInputVars"]["items"]["type"], "string")

    # ------------------------------------------------------------------ #
    # 5. Backwards compat                                                 #
    # ------------------------------------------------------------------ #

    def test_v03_config_still_validates(self):
        v03_doc = {
            "version": "0.1",
            "vendors": {
                "gemini": {"defaultModel": "gemini-2.5-flash"}
            },
            "costCeiling": 0.10
        }
        try:
            validate(instance=v03_doc, schema=self.schema)
        except ValidationError as e:
            self.fail(f"v0.3 config failed v0.4 schema: {e.message}")

    def test_v04_config_with_inject_attack_validates(self):
        doc = {
            "version": "0.1",
            "vendors": {
                "gemini": {"defaultModel": "gemini-2.5-flash"}
            },
            "costCeiling": 0.10,
            "eval": {
                "injectAttack": {
                    "enabled": True,
                    "fixtures": ["direct-override-v1", "role-assertion-v1"],
                    "costCeiling": 0.20
                }
            },
            "audit": {
                "injectionResistance": {
                    "userInputVars": ["userDreamText", "userMessage"]
                }
            }
        }
        try:
            validate(instance=doc, schema=self.schema)
        except ValidationError as e:
            self.fail(f"v0.4 config with injectAttack fields failed: {e.message}")


if __name__ == "__main__":
    unittest.main()
