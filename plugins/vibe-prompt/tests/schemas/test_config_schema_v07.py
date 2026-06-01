"""
Task 7 (v0.7) — TDD tests for config.schema.json v0.7 extensions.

Asserts:
  1. scan.workspaceDetection enum (auto | force-single | force-monorepo),
     default auto
  2. scan.excludes string array
  3. audit.f6.modelIdExceptions string array
  4. remediate.applyInlineToRegistry boolean, default false
  5. remediate.applyTypedRenderer boolean, default false
  6. remediate.applyModelConsolidation boolean, default false
  7. Backward compat: v0.6 config validates
"""

import json
import pathlib
import unittest

from jsonschema import validate, ValidationError

SCHEMAS_DIR = pathlib.Path(__file__).parent.parent.parent / "schemas"
SCHEMA_PATH = SCHEMAS_DIR / "config.schema.json"


def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def _minimal_config(extra=None):
    doc = {
        "version": "0.1",
        "vendors": {"gemini": {"defaultModel": "gemini-2.5-flash"}},
        "costCeiling": 0.10,
    }
    if extra:
        doc.update(extra)
    return doc


class TestConfigV07Scan(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_scan_property_declared(self):
        self.assertIn("scan", self.schema["properties"])

    def test_scan_workspaceDetection_enum(self):
        scan_props = self.schema["properties"]["scan"]["properties"]
        wd = scan_props["workspaceDetection"]
        for expected in ["auto", "force-single", "force-monorepo"]:
            self.assertIn(expected, wd["enum"])

    def test_scan_workspaceDetection_default_auto(self):
        scan_props = self.schema["properties"]["scan"]["properties"]
        self.assertEqual(
            scan_props["workspaceDetection"].get("default"), "auto"
        )

    def test_scan_excludes_is_string_array(self):
        scan_props = self.schema["properties"]["scan"]["properties"]
        excludes = scan_props["excludes"]
        self.assertEqual(excludes["type"], "array")
        self.assertEqual(excludes["items"]["type"], "string")

    def test_config_with_scan_validates(self):
        doc = _minimal_config(
            extra={
                "scan": {
                    "workspaceDetection": "auto",
                    "excludes": ["vibe-*/", "_ARCHIVE_*/"],
                }
            }
        )
        validate(instance=doc, schema=self.schema)

    def test_config_with_invalid_workspaceDetection_rejected(self):
        doc = _minimal_config(
            extra={"scan": {"workspaceDetection": "polyrepo"}}
        )
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)


class TestConfigV07AuditF6(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_audit_f6_property_declared(self):
        audit_props = self.schema["properties"]["audit"]["properties"]
        self.assertIn("f6", audit_props)

    def test_audit_f6_modelIdExceptions_is_string_array(self):
        f6 = self.schema["properties"]["audit"]["properties"]["f6"][
            "properties"
        ]
        exceptions = f6["modelIdExceptions"]
        self.assertEqual(exceptions["type"], "array")
        self.assertEqual(exceptions["items"]["type"], "string")

    def test_config_with_audit_f6_validates(self):
        doc = _minimal_config(
            extra={
                "audit": {
                    "f6": {
                        "modelIdExceptions": [
                            "gemini-3.1-pro",
                            "internal-test-model",
                        ]
                    }
                }
            }
        )
        validate(instance=doc, schema=self.schema)


class TestConfigV07RemediateCategoryD(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_applyInlineToRegistry_declared(self):
        rem_props = self.schema["properties"]["remediate"]["properties"]
        self.assertIn("applyInlineToRegistry", rem_props)
        self.assertEqual(rem_props["applyInlineToRegistry"]["type"], "boolean")
        self.assertEqual(
            rem_props["applyInlineToRegistry"].get("default"), False
        )

    def test_applyTypedRenderer_declared(self):
        rem_props = self.schema["properties"]["remediate"]["properties"]
        self.assertIn("applyTypedRenderer", rem_props)
        self.assertEqual(rem_props["applyTypedRenderer"]["type"], "boolean")
        self.assertEqual(
            rem_props["applyTypedRenderer"].get("default"), False
        )

    def test_applyModelConsolidation_declared(self):
        rem_props = self.schema["properties"]["remediate"]["properties"]
        self.assertIn("applyModelConsolidation", rem_props)
        self.assertEqual(
            rem_props["applyModelConsolidation"]["type"], "boolean"
        )
        self.assertEqual(
            rem_props["applyModelConsolidation"].get("default"), False
        )

    def test_config_with_category_d_toggles_validates(self):
        doc = _minimal_config(
            extra={
                "remediate": {
                    "applyInlineToRegistry": True,
                    "applyTypedRenderer": False,
                    "applyModelConsolidation": True,
                }
            }
        )
        validate(instance=doc, schema=self.schema)


class TestConfigV07BackwardCompat(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_v06_config_validates(self):
        doc = {
            "version": "0.1",
            "vendors": {
                "gemini": {
                    "defaultModel": "gemini-2.5-flash",
                    "fallbackModel": "gemini-2.5-pro",
                }
            },
            "costCeiling": 0.10,
            "fixturePath": "fixtures/",
            "audit": {
                "varOriginOverrides": {"unsanitized_user_input": "user-controlled"},
                "f13": {
                    "outputFormatExceptions": ["synastry_report"]
                },
            },
            "remediate": {
                "autoApplyThreshold": 0.90,
                "stageThreshold": 0.70,
                "backupRetentionDays": 30,
                "autoHandoffVibeSec": True,
                "applyVoiceFrameFixes": False,
            },
        }
        validate(instance=doc, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
