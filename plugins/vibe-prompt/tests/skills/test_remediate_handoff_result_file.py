"""
Task 21 — TDD tests for handoff-vibe-sec result file written by :remediate.

Asserts:
- SKILL.md documents writing result to
  .vibe-prompt/remediate/state/handoff-vibe-sec-<timestamp>.json
- File schema fields: runId, timestamp, triggeringFinding, vibeSecVersion,
  vibeSecFindings, exitCode, scope
- File validates against handoff-vibe-sec.schema.json (Task 6)
"""

import json
import pathlib
import unittest

PLUGIN_ROOT = pathlib.Path(__file__).parent.parent.parent
SKILLS_DIR = PLUGIN_ROOT / "skills"
SCHEMAS_DIR = PLUGIN_ROOT / "schemas"
REMEDIATE_SKILL = SKILLS_DIR / "remediate" / "SKILL.md"
HANDOFF_SCHEMA = SCHEMAS_DIR / "handoff-vibe-sec.schema.json"


class TestRemediateHandoffResultFile(unittest.TestCase):

    def setUp(self):
        self.skill = REMEDIATE_SKILL.read_text(encoding="utf-8")
        self.lower = self.skill.lower()
        self.assertTrue(
            HANDOFF_SCHEMA.exists(),
            f"handoff-vibe-sec.schema.json must exist (Task 6) at {HANDOFF_SCHEMA}",
        )
        with HANDOFF_SCHEMA.open("r", encoding="utf-8") as f:
            self.schema = json.load(f)

    def test_skill_references_handoff_result_path(self):
        # Path: .vibe-prompt/remediate/state/handoff-vibe-sec-<timestamp>.json
        self.assertIn(
            "handoff-vibe-sec-",
            self.skill,
            "SKILL.md must reference handoff-vibe-sec-<timestamp>.json filename",
        )
        self.assertIn(
            ".vibe-prompt/remediate/state/",
            self.skill,
            "SKILL.md must write handoff result file under .vibe-prompt/remediate/state/",
        )

    def test_skill_references_handoff_schema(self):
        self.assertIn(
            "handoff-vibe-sec.schema.json",
            self.skill,
            "SKILL.md must reference handoff-vibe-sec.schema.json for validation",
        )

    # --- Field coverage in SKILL.md ---
    def test_skill_documents_runid_field(self):
        self.assertIn("runId", self.skill)

    def test_skill_documents_timestamp_field(self):
        idx = self.skill.find("handoff-vibe-sec-")
        section = self.skill[max(0, idx - 200):idx + 2000].lower()
        self.assertIn("timestamp", section)

    def test_skill_documents_triggering_finding(self):
        self.assertIn("triggeringFinding", self.skill)

    def test_skill_documents_vibe_sec_version_field(self):
        self.assertIn("vibeSecVersion", self.skill)

    def test_skill_documents_vibe_sec_findings_field(self):
        self.assertIn("vibeSecFindings", self.skill)

    def test_skill_documents_exit_code_field(self):
        self.assertIn("exitCode", self.skill)

    def test_skill_documents_scope_field(self):
        # scope is optional - omitted when fallback to full audit
        self.assertIn("scope", self.skill)

    # --- Verify the schema covers the same fields ---
    def test_schema_has_required_handoff_fields(self):
        required = self.schema.get("required", [])
        for field in [
            "runId",
            "timestamp",
            "triggeringFinding",
            "vibeSecVersion",
            "vibeSecFindings",
            "exitCode",
        ]:
            self.assertIn(
                field, required,
                f"handoff-vibe-sec.schema.json must require {field}",
            )

    def test_schema_has_scope_property(self):
        props = self.schema.get("properties", {})
        self.assertIn(
            "scope", props,
            "handoff-vibe-sec.schema.json must declare optional scope property",
        )

    def test_sample_handoff_file_validates_against_schema(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not installed")

        sample = {
            "runId": "handoff-2026-06-15-1430",
            "timestamp": "2026-06-15T14:30:00Z",
            "triggeringFinding": "F12-oneirocriton-2026-06-15",
            "vibeSecVersion": "0.6.0",
            "vibeSecFindings": [],
            "exitCode": 0,
            "scope": "user-input-boundary",
        }
        jsonschema.validate(sample, self.schema)

    def test_sample_handoff_file_validates_with_omitted_scope(self):
        """When scope falls back to full audit, scope is omitted."""
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not installed")

        sample = {
            "runId": "handoff-2026-06-15-1430",
            "timestamp": "2026-06-15T14:30:00Z",
            "triggeringFinding": "F12-oneirocriton-2026-06-15",
            "vibeSecVersion": "0.5.0",
            "vibeSecFindings": [],
            "exitCode": 0,
        }
        jsonschema.validate(sample, self.schema)


if __name__ == "__main__":
    unittest.main()
