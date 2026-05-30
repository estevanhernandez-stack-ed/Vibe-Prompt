"""
Task 5 (v0.6) — TDD tests for config.schema.json v0.6 extensions.

Asserts:
  1. remediate.autoHandoffVibeSec boolean (default false)
  2. remediate.applyVoiceFrameFixes boolean (default false)
  3. audit.f13.outputFormatExceptions string array
  4. Backward compat: v0.5 config doc still validates
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


class TestConfigV06RemediateAutoHandoff(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_autoHandoffVibeSec_field_exists(self):
        remediate_props = self.schema["properties"]["remediate"]["properties"]
        self.assertIn("autoHandoffVibeSec", remediate_props)

    def test_autoHandoffVibeSec_is_boolean(self):
        remediate_props = self.schema["properties"]["remediate"]["properties"]
        self.assertEqual(remediate_props["autoHandoffVibeSec"]["type"], "boolean")

    def test_autoHandoffVibeSec_default_false(self):
        remediate_props = self.schema["properties"]["remediate"]["properties"]
        self.assertEqual(remediate_props["autoHandoffVibeSec"]["default"], False)

    def test_config_with_autoHandoffVibeSec_true_validates(self):
        doc = _minimal_doc({"remediate": {"autoHandoffVibeSec": True}})
        validate(instance=doc, schema=self.schema)

    def test_config_with_autoHandoffVibeSec_false_validates(self):
        doc = _minimal_doc({"remediate": {"autoHandoffVibeSec": False}})
        validate(instance=doc, schema=self.schema)


class TestConfigV06RemediateApplyVoiceFrame(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_applyVoiceFrameFixes_field_exists(self):
        remediate_props = self.schema["properties"]["remediate"]["properties"]
        self.assertIn("applyVoiceFrameFixes", remediate_props)

    def test_applyVoiceFrameFixes_is_boolean(self):
        remediate_props = self.schema["properties"]["remediate"]["properties"]
        self.assertEqual(
            remediate_props["applyVoiceFrameFixes"]["type"], "boolean"
        )

    def test_applyVoiceFrameFixes_default_false(self):
        remediate_props = self.schema["properties"]["remediate"]["properties"]
        self.assertEqual(
            remediate_props["applyVoiceFrameFixes"]["default"], False
        )

    def test_config_with_applyVoiceFrameFixes_true_validates(self):
        doc = _minimal_doc({"remediate": {"applyVoiceFrameFixes": True}})
        validate(instance=doc, schema=self.schema)


class TestConfigV06AuditF13OutputFormatExceptions(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_f13_section_exists_under_audit(self):
        audit_props = self.schema["properties"]["audit"]["properties"]
        self.assertIn("f13", audit_props)

    def test_outputFormatExceptions_field_exists(self):
        audit_props = self.schema["properties"]["audit"]["properties"]
        f13_props = audit_props["f13"]["properties"]
        self.assertIn("outputFormatExceptions", f13_props)

    def test_outputFormatExceptions_is_array(self):
        audit_props = self.schema["properties"]["audit"]["properties"]
        f13_props = audit_props["f13"]["properties"]
        self.assertEqual(f13_props["outputFormatExceptions"]["type"], "array")

    def test_outputFormatExceptions_items_are_strings(self):
        audit_props = self.schema["properties"]["audit"]["properties"]
        f13_props = audit_props["f13"]["properties"]
        self.assertEqual(
            f13_props["outputFormatExceptions"]["items"]["type"], "string"
        )

    def test_config_with_outputFormatExceptions_validates(self):
        doc = _minimal_doc(
            {
                "audit": {
                    "f13": {
                        "outputFormatExceptions": [
                            "flex_output_prompt",
                            "tarot_freeform",
                        ]
                    }
                }
            }
        )
        validate(instance=doc, schema=self.schema)

    def test_config_with_empty_outputFormatExceptions_validates(self):
        doc = _minimal_doc(
            {"audit": {"f13": {"outputFormatExceptions": []}}}
        )
        validate(instance=doc, schema=self.schema)

    def test_outputFormatExceptions_with_non_string_rejected(self):
        doc = _minimal_doc(
            {"audit": {"f13": {"outputFormatExceptions": [42]}}}
        )
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)


class TestConfigV06BackwardCompat(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_v05_minimal_config_validates(self):
        doc = _minimal_doc()
        validate(instance=doc, schema=self.schema)

    def test_v05_full_config_with_remediate_thresholds(self):
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

    def test_v06_full_config_with_all_new_fields(self):
        doc = _minimal_doc(
            {
                "remediate": {
                    "autoApplyThreshold": 0.90,
                    "stageThreshold": 0.70,
                    "backupRetentionDays": 30,
                    "autoHandoffVibeSec": True,
                    "applyVoiceFrameFixes": False,
                },
                "audit": {
                    "injectionResistance": {"userInputVars": ["dreamText"]},
                    "varOriginOverrides": {
                        "knowledgeContext": "system-injected"
                    },
                    "f13": {
                        "outputFormatExceptions": ["flexible_oracle_prompt"]
                    },
                },
            }
        )
        validate(instance=doc, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
