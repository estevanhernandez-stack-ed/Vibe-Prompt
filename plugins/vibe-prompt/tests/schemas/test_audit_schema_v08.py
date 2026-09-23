"""
v0.8 — audit.schema.json + config.schema.json extensions.

Asserts:
  1. findings[].id enum gains F14 and F6-retiring-model (additive)
  2. findings[].subCase enum carries the four F14 sub-cases
  3. evidence items accept modelValue / modelResolution / retirementDate /
     retirementDateKind / daysRemaining
  4. Valid F14 and F6-retiring-model findings validate; bad enums fail
  5. config audit.f14.exceptions is a string array
  6. Back-compat: a v0.7-shaped audit.json and config still validate
"""

import json
import pathlib
import unittest

from jsonschema import validate, ValidationError

SCHEMAS_DIR = pathlib.Path(__file__).parent.parent.parent / "schemas"


def _load(name):
    with open(SCHEMAS_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def _audit(finding):
    return {
        "version": "0.1",
        "auditedAt": "2026-09-22T00:00:00Z",
        "inventoryRef": ".vibe-prompt/state/inventory.json",
        "findings": [finding],
        "summary": {"totalFindings": 1, "byCategory": {"high": 1}},
    }


F14_FINDING = {
    "id": "F14",
    "subCase": "F14-positional-content-read",
    "smell": "model-migration-api-breakage",
    "severity": "high",
    "evidence": [{
        "file": "src/lib/claude.ts",
        "line": 42,
        "note": "response.content[0].text",
        "modelValue": "process.env.CLAUDE_MODEL",
        "modelResolution": "unresolved",
    }],
    "recommendation": "Select blocks by type.",
    "composerIdentifier": None,
}

RETIRING_FINDING = {
    "id": "F6-retiring-model",
    "smell": "retiring-model",
    "severity": "medium",
    "evidence": [{
        "file": "config.json",
        "line": 3,
        "modelValue": "claude-haiku-4-5-20251001",
        "retirementDate": "2026-10-15",
        "retirementDateKind": "floor",
        "daysRemaining": 23,
    }],
    "recommendation": "Move to the recommended replacement.",
}


class TestAuditSchemaV08(unittest.TestCase):

    def setUp(self):
        self.schema = _load("audit.schema.json")
        self.finding_props = self.schema["properties"]["findings"]["items"]["properties"]

    def test_id_enum_additive(self):
        ids = self.finding_props["id"]["enum"]
        for fid in ["F14", "F6-retiring-model"]:
            self.assertIn(fid, ids)
        # v0.7 ids still present
        for fid in ["F1", "F1b", "F6", "F6-suspect-model", "F12", "F13"]:
            self.assertIn(fid, ids)

    def test_sub_case_enum(self):
        self.assertEqual(
            sorted(self.finding_props["subCase"]["enum"]),
            sorted([
                "F14-thinking-param", "F14-forced-tool-choice",
                "F14-legacy-computer-tool", "F14-positional-content-read",
            ]),
        )

    def test_evidence_item_fields(self):
        ev = self.finding_props["evidence"]["items"]["properties"]
        for field in ["modelValue", "modelResolution", "retirementDate",
                      "retirementDateKind", "daysRemaining"]:
            self.assertIn(field, ev)
        self.assertEqual(
            sorted(ev["modelResolution"]["enum"]),
            ["older-pinned", "resolved", "unresolved"],
        )
        self.assertEqual(
            sorted(ev["retirementDateKind"]["enum"]),
            ["floor", "retired", "scheduled"],
        )

    def test_f14_finding_validates(self):
        validate(instance=_audit(F14_FINDING), schema=self.schema)

    def test_retiring_finding_validates(self):
        validate(instance=_audit(RETIRING_FINDING), schema=self.schema)

    def test_bad_sub_case_rejected(self):
        bad = dict(F14_FINDING, subCase="F14-temperature")
        with self.assertRaises(ValidationError):
            validate(instance=_audit(bad), schema=self.schema)

    def test_bad_model_resolution_rejected(self):
        bad = json.loads(json.dumps(F14_FINDING))
        bad["evidence"][0]["modelResolution"] = "guessed"
        with self.assertRaises(ValidationError):
            validate(instance=_audit(bad), schema=self.schema)

    def test_v07_audit_still_validates(self):
        v07 = {
            "id": "F6-suspect-model",
            "smell": "suspect-model",
            "severity": "medium",
            "evidence": [{"file": "scripts/gen.mjs", "line": 87}],
            "recommendation": "Verify the id.",
            "composerIdentifier": None,
            "workspaceIdentifier": None,
        }
        validate(instance=_audit(v07), schema=self.schema)


class TestConfigSchemaV08(unittest.TestCase):

    def setUp(self):
        self.schema = _load("config.schema.json")

    def _config(self, audit):
        return {
            "version": "0.1",
            "vendors": {"gemini": {"defaultModel": "gemini-2.5-flash"}},
            "costCeiling": 0.10,
            "audit": audit,
        }

    def test_f14_exceptions_declared(self):
        f14 = self.schema["properties"]["audit"]["properties"]["f14"]
        exc = f14["properties"]["exceptions"]
        self.assertEqual(exc["type"], "array")
        self.assertEqual(exc["items"]["type"], "string")

    def test_f14_exceptions_validate(self):
        validate(
            instance=self._config({"f14": {"exceptions": ["src/a.ts:12", "natal_interpretation"]}}),
            schema=self.schema,
        )

    def test_f14_exceptions_reject_non_string(self):
        with self.assertRaises(ValidationError):
            validate(instance=self._config({"f14": {"exceptions": [12]}}), schema=self.schema)

    def test_v07_config_still_validates(self):
        validate(
            instance=self._config({"f6": {"modelIdExceptions": ["gemini-3.1-pro"]},
                                   "f13": {"outputFormatExceptions": ["x"]}}),
            schema=self.schema,
        )


if __name__ == "__main__":
    unittest.main()
