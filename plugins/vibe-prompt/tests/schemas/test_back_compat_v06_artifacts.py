"""
v0.7 back-compat regression tests.

Catches the three back-compat regressions the v0.7 build agents missed (caught by
the adversarial backward-compat verifier, post-build). These tests pin the
contracts that real v0.5/v0.6 Celestia3 artifacts depend on so they cannot be
broken again silently.

1. audit.schema.json — injectionResistance accepts both v0.6 integer shape and
   v0.7 {value, rationale} object shape via oneOf.
2. remediate-result.schema.json — subCategory accepts null (v0.6 emits null on
   non-voice-frame diffs).
3. remediate-result.schema.json — inlineOnlyDiffs[] accepts sentinel rows with
   {findingId, findingCategory: null, postApplyRecommendation} (v0.5/v0.6 shape).
4. remediate-result.schema.json — backupBatchPath accepts null.
"""

import json
import pathlib
import unittest

from jsonschema import validate, ValidationError

SCHEMAS_DIR = pathlib.Path(__file__).parent.parent.parent / "schemas"
AUDIT_SCHEMA = json.loads((SCHEMAS_DIR / "audit.schema.json").read_text(encoding="utf-8"))
REMEDIATE_SCHEMA = json.loads((SCHEMAS_DIR / "remediate-result.schema.json").read_text(encoding="utf-8"))


def _audit_doc(injection_resistance):
    return {
        "version": "0.1",
        "auditedAt": "2026-06-01T00:00:00Z",
        "pluginVersion": "0.7",
        "inventoryRef": ".vibe-prompt/state/inventory.json",
        "findings": [],
        "summary": {"totalFindings": 0, "byCategory": {"high": 0, "medium": 0, "low": 0, "advisory": 0}},
        "auditGrade": {
            "perPrompt": {
                "prompt_a": {
                    "composite": 8,
                    "dimensions": {
                        "schemaTightness": 9,
                        "personaConsistency": 8,
                        "instructionClarity": 7,
                        "tokenEfficiency": 8,
                        "injectionResistance": injection_resistance,
                    },
                    "appliedFindings": [],
                }
            },
            "appComposite": 8,
        },
    }


def _remediate_doc(extra_top=None, staged=None, inline=None, backup_batch_path=""):
    doc = {
        "runId": "remediate-2026-06-01-back-compat",
        "timestamp": "2026-06-01T00:00:00Z",
        "auditRunId": "audit-2026-06-01-back-compat",
        "totalFindings": 1,
        "diffsByCategory": {"categoryA": 0, "categoryB": 0, "categoryC": 0},
        "appliedDiffs": [],
        "stagedDiffs": staged or [],
        "inlineOnlyDiffs": inline or [],
        "backupBatchPath": backup_batch_path,
    }
    if extra_top:
        doc.update(extra_top)
    return doc


class V06InjectionResistanceIntegerBackCompat(unittest.TestCase):
    """v0.6 emits injectionResistance as plain integer; v0.7 must continue to accept it."""

    def test_v06_integer_shape_validates(self):
        validate(_audit_doc(10), AUDIT_SCHEMA)

    def test_v07_object_shape_validates(self):
        validate(
            _audit_doc({"value": 9, "rationale": "Strong defense block + delimiters"}),
            AUDIT_SCHEMA,
        )

    def test_invalid_string_shape_rejected(self):
        with self.assertRaises(ValidationError):
            validate(_audit_doc("ten"), AUDIT_SCHEMA)

    def test_invalid_object_without_value_rejected(self):
        with self.assertRaises(ValidationError):
            validate(_audit_doc({"rationale": "missing value field"}), AUDIT_SCHEMA)


class V06SubCategoryNullableBackCompat(unittest.TestCase):
    """v0.6 emits subCategory: null on non-voice-frame Category C diffs."""

    def test_subcategory_null_validates(self):
        staged = [{
            "findingId": "F13-synastry_report-2026-05-29",
            "findingCategory": "C",
            "subCategory": None,
            "confidence": 0.87,
            "targetFile": "src/lib/ConfigService.ts",
        }]
        validate(_remediate_doc(staged=staged), REMEDIATE_SCHEMA)

    def test_subcategory_string_still_validates(self):
        staged = [{
            "findingId": "F2-natal-voice-frame",
            "findingCategory": "B",
            "subCategory": "voice-frame-rewrite",
            "confidence": 0.65,
            "targetFile": "src/lib/ConfigService.ts",
        }]
        validate(_remediate_doc(staged=staged), REMEDIATE_SCHEMA)


class V06InlineOnlySentinelBackCompat(unittest.TestCase):
    """v0.5/v0.6 inlineOnlyDiffs[] sentinel rows must validate."""

    def test_sentinel_row_validates(self):
        inline = [
            {"findingId": "F1", "findingCategory": None,
             "postApplyRecommendation": "Move inline systemInstruction literals to registry. Deferred."},
            {"findingId": "F6", "findingCategory": None,
             "postApplyRecommendation": "Consolidate model identifier. Deferred."},
            {"findingId": "F12-deterministic-not-fire", "findingCategory": None,
             "postApplyRecommendation": "F12 DETERMINISTIC not-fire (v0.6 API-parameter-aware)."},
        ]
        validate(_remediate_doc(inline=inline), REMEDIATE_SCHEMA)

    def test_full_diff_in_inline_still_validates(self):
        """v0.7+ may put a real diff (not sentinel) into inlineOnlyDiffs[]; both shapes coexist."""
        inline = [{
            "findingId": "F4-typed-renderer",
            "findingCategory": "D-2",
            "confidence": 0.75,
            "targetFile": "src/lib/registry.ts",
            "diffBody": "--- a/src/lib/registry.ts\n+++ b/src/lib/registry.ts\n",
        }]
        validate(_remediate_doc(inline=inline), REMEDIATE_SCHEMA)

    def test_sentinel_missing_required_field_rejected(self):
        """Sentinel must still carry findingId + postApplyRecommendation."""
        inline = [{"findingId": "F1", "findingCategory": None}]  # missing postApplyRecommendation
        with self.assertRaises(ValidationError):
            validate(_remediate_doc(inline=inline), REMEDIATE_SCHEMA)


class V06BackupBatchPathNullableBackCompat(unittest.TestCase):
    """v0.6 emits backupBatchPath: null when no backup was taken."""

    def test_backup_batch_path_null_validates(self):
        validate(_remediate_doc(backup_batch_path=None), REMEDIATE_SCHEMA)

    def test_backup_batch_path_string_validates(self):
        validate(_remediate_doc(backup_batch_path=".vibe-prompt/remediate/backups/2026-06-01"), REMEDIATE_SCHEMA)


class CelestiaArtifactsValidateEndToEnd(unittest.TestCase):
    """If real Celestia3 v0.6 artifacts are on disk, validate them end-to-end."""

    CELESTIA_AUDIT = pathlib.Path("C:/Users/estev/Projects/Celestia3/.vibe-prompt/state/audit.json")
    CELESTIA_REMEDIATE_V05 = pathlib.Path(
        "C:/Users/estev/Projects/Celestia3/.vibe-prompt/remediate/state/remediate-2026-05-29-1005.json"
    )
    CELESTIA_REMEDIATE_V06 = pathlib.Path(
        "C:/Users/estev/Projects/Celestia3/.vibe-prompt/remediate/state/remediate-2026-05-29-1800.json"
    )

    def test_celestia_v06_audit_validates(self):
        if not self.CELESTIA_AUDIT.exists():
            self.skipTest("Celestia3 audit artifact not on disk in this environment")
        validate(json.loads(self.CELESTIA_AUDIT.read_text(encoding="utf-8")), AUDIT_SCHEMA)

    def test_celestia_v05_remediate_validates(self):
        if not self.CELESTIA_REMEDIATE_V05.exists():
            self.skipTest("Celestia3 v0.5 remediate artifact not on disk in this environment")
        validate(json.loads(self.CELESTIA_REMEDIATE_V05.read_text(encoding="utf-8")), REMEDIATE_SCHEMA)

    def test_celestia_v06_remediate_validates(self):
        if not self.CELESTIA_REMEDIATE_V06.exists():
            self.skipTest("Celestia3 v0.6 remediate artifact not on disk in this environment")
        validate(json.loads(self.CELESTIA_REMEDIATE_V06.read_text(encoding="utf-8")), REMEDIATE_SCHEMA)


if __name__ == "__main__":
    unittest.main()
