"""
Task 4 — TDD tests for config.schema.json v0.5 extensions.

Asserts:
  1. remediate.autoApplyThreshold number with default 0.90
  2. remediate.stageThreshold number with default 0.70
  3. remediate.backupRetentionDays integer with default 30
  4. audit.varOriginOverrides object additionalProperties enum (user-controlled | system-injected)
  5. Backward compat: v0.4 config doc still validates
"""

import json
import pathlib
import unittest

from jsonschema import validate, ValidationError

SCHEMAS_DIR = pathlib.Path(__file__).parent.parent.parent / "schemas"
CONFIG_SCHEMA_PATH = SCHEMAS_DIR / "config.schema.json"


def load_schema():
    with open(CONFIG_SCHEMA_PATH) as f:
        return json.load(f)


def _minimal_doc(extra=None):
    doc = {
        "version": "0.1",
        "vendors": {"gemini": {"defaultModel": "gemini-1.5-flash"}},
        "costCeiling": 0.05,
    }
    if extra:
        doc.update(extra)
    return doc


class TestConfigV05RemediateSection(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_remediate_section_exists(self):
        self.assertIn("remediate", self.schema["properties"])

    def test_autoApplyThreshold_field_exists(self):
        remediate_props = self.schema["properties"]["remediate"]["properties"]
        self.assertIn("autoApplyThreshold", remediate_props)

    def test_autoApplyThreshold_is_number(self):
        remediate_props = self.schema["properties"]["remediate"]["properties"]
        self.assertEqual(remediate_props["autoApplyThreshold"]["type"], "number")

    def test_autoApplyThreshold_default_value(self):
        remediate_props = self.schema["properties"]["remediate"]["properties"]
        self.assertEqual(remediate_props["autoApplyThreshold"]["default"], 0.90)

    def test_stageThreshold_field_exists(self):
        remediate_props = self.schema["properties"]["remediate"]["properties"]
        self.assertIn("stageThreshold", remediate_props)

    def test_stageThreshold_default_value(self):
        remediate_props = self.schema["properties"]["remediate"]["properties"]
        self.assertEqual(remediate_props["stageThreshold"]["default"], 0.70)

    def test_backupRetentionDays_field_exists(self):
        remediate_props = self.schema["properties"]["remediate"]["properties"]
        self.assertIn("backupRetentionDays", remediate_props)

    def test_backupRetentionDays_is_integer(self):
        remediate_props = self.schema["properties"]["remediate"]["properties"]
        self.assertEqual(remediate_props["backupRetentionDays"]["type"], "integer")

    def test_backupRetentionDays_default_30(self):
        remediate_props = self.schema["properties"]["remediate"]["properties"]
        self.assertEqual(remediate_props["backupRetentionDays"]["default"], 30)

    def test_remediate_full_section_validates(self):
        doc = _minimal_doc(
            {
                "remediate": {
                    "autoApplyThreshold": 0.92,
                    "stageThreshold": 0.65,
                    "backupRetentionDays": 14,
                }
            }
        )
        validate(instance=doc, schema=self.schema)

    def test_invalid_backupRetentionDays_type_rejected(self):
        doc = _minimal_doc(
            {"remediate": {"backupRetentionDays": "thirty"}}
        )
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)


class TestConfigV05VarOriginOverrides(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_audit_varOriginOverrides_field_exists(self):
        audit_props = self.schema["properties"]["audit"]["properties"]
        self.assertIn("varOriginOverrides", audit_props)

    def test_varOriginOverrides_is_object(self):
        audit_props = self.schema["properties"]["audit"]["properties"]
        self.assertEqual(audit_props["varOriginOverrides"]["type"], "object")

    def test_varOriginOverrides_additionalProperties_enum(self):
        audit_props = self.schema["properties"]["audit"]["properties"]
        ap = audit_props["varOriginOverrides"]["additionalProperties"]
        enum_vals = ap["enum"]
        self.assertIn("user-controlled", enum_vals)
        self.assertIn("system-injected", enum_vals)

    def test_varOriginOverrides_valid_doc_validates(self):
        doc = _minimal_doc(
            {
                "audit": {
                    "varOriginOverrides": {
                        "knowledgeContext": "system-injected",
                        "dreamText": "user-controlled",
                    }
                }
            }
        )
        validate(instance=doc, schema=self.schema)

    def test_varOriginOverrides_invalid_value_rejected(self):
        doc = _minimal_doc(
            {"audit": {"varOriginOverrides": {"x": "alien"}}}
        )
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)


class TestConfigV05BackwardCompat(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_v04_minimal_config_validates(self):
        doc = _minimal_doc()
        validate(instance=doc, schema=self.schema)

    def test_v04_with_injectAttack_and_injectionResistance_validates(self):
        doc = _minimal_doc(
            {
                "eval": {
                    "injectAttack": {
                        "enabled": True,
                        "fixtures": ["fixtures/x.json"],
                        "costCeiling": 0.10,
                    }
                },
                "audit": {
                    "injectionResistance": {
                        "userInputVars": ["userText"]
                    }
                },
            }
        )
        validate(instance=doc, schema=self.schema)

    def test_v05_full_config_with_remediate_and_overrides(self):
        doc = _minimal_doc(
            {
                "remediate": {
                    "autoApplyThreshold": 0.85,
                    "stageThreshold": 0.60,
                    "backupRetentionDays": 60,
                },
                "audit": {
                    "injectionResistance": {"userInputVars": ["dreamText"]},
                    "varOriginOverrides": {
                        "knowledgeContext": "system-injected"
                    },
                },
            }
        )
        validate(instance=doc, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
