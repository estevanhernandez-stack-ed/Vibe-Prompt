"""
Task 4 (v0.6) — TDD tests for pending-fix.schema.json v0.6 extensions.

Asserts:
  1. findingCategory enum gains documented sub-category notation —
     `B-voice-frame` as valid value alongside A, B, C.
  2. voiceFrameRewriteRationale optional string.
  3. Backward compat: v0.5 pending-fix front-matter validates.
"""

import json
import pathlib
import unittest

from jsonschema import validate, ValidationError

SCHEMAS_DIR = pathlib.Path(__file__).parent.parent.parent / "schemas"
PENDING_FIX_PATH = SCHEMAS_DIR / "pending-fix.schema.json"


def load_schema():
    with open(PENDING_FIX_PATH) as f:
        return json.load(f)


def _minimal_doc(extra=None, category="B"):
    doc = {
        "findingId": "F2-natal_interpretation-2026-06-15",
        "findingCategory": category,
        "confidence": 0.65,
        "targetFile": "src/lib/ConfigService.ts",
        "targetRange": "L67-L102",
        "recommendationSource": "audit-2026-06-15-1400",
    }
    if extra:
        doc.update(extra)
    return doc


class TestPendingFixV06BVoiceFrameCategory(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_B_voice_frame_in_findingCategory_enum(self):
        enum_vals = self.schema["properties"]["findingCategory"]["enum"]
        self.assertIn("B-voice-frame", enum_vals)

    def test_existing_A_B_C_preserved(self):
        enum_vals = self.schema["properties"]["findingCategory"]["enum"]
        for expected in ["A", "B", "C"]:
            self.assertIn(expected, enum_vals)

    def test_pending_fix_with_B_voice_frame_validates(self):
        doc = _minimal_doc(category="B-voice-frame")
        validate(instance=doc, schema=self.schema)

    def test_pending_fix_with_invalid_subcategory_rejected(self):
        doc = _minimal_doc(category="B-mystery")
        with self.assertRaises(ValidationError):
            validate(instance=doc, schema=self.schema)


class TestPendingFixV06VoiceFrameRewriteRationale(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_voiceFrameRewriteRationale_field_exists(self):
        self.assertIn("voiceFrameRewriteRationale", self.schema["properties"])

    def test_voiceFrameRewriteRationale_is_string(self):
        self.assertEqual(
            self.schema["properties"]["voiceFrameRewriteRationale"]["type"],
            "string",
        )

    def test_voiceFrameRewriteRationale_is_optional(self):
        required = self.schema.get("required", [])
        self.assertNotIn("voiceFrameRewriteRationale", required)

    def test_pending_fix_with_voiceFrameRewriteRationale_validates(self):
        doc = _minimal_doc(
            extra={
                "voiceFrameRewriteRationale": (
                    "Rewrites 'quatrain-style narrative' to 'first-person reflection' to align "
                    "with global directive's 'plain modern language, warm friend' rule."
                )
            },
            category="B-voice-frame",
        )
        validate(instance=doc, schema=self.schema)


class TestPendingFixV06BackwardCompat(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_v05_minimal_pending_with_A_validates(self):
        doc = _minimal_doc(category="A")
        validate(instance=doc, schema=self.schema)

    def test_v05_minimal_pending_with_B_validates(self):
        doc = _minimal_doc(category="B")
        validate(instance=doc, schema=self.schema)

    def test_v05_minimal_pending_with_C_validates(self):
        doc = _minimal_doc(category="C")
        validate(instance=doc, schema=self.schema)

    def test_v05_full_pending_validates(self):
        doc = _minimal_doc(
            extra={
                "backupPath": ".vibe-prompt/remediate/backup/...",
                "postApplyRecommendation": "Re-run /vibe-prompt:eval --prompts natal",
                "versionBumpRequired": True,
                "suggestedVersion": "3.6.0",
            },
            category="B",
        )
        validate(instance=doc, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
