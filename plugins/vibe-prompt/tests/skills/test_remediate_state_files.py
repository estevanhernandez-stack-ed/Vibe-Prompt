"""
Task 22 — TDD tests for state file layout in skills/remediate/SKILL.md.

Asserts the SKILL.md documents:
  - .vibe-prompt/remediate/state/runs.jsonl (append-only ledger)
  - Each entry shape with timestamp, runId, action, findingIds, confidence, fileTouched, backupPath
  - Backup dir naming convention .vibe-prompt/remediate/backup/<ISO-timestamp>/
  - Pending dir layout .vibe-prompt/remediate/pending/<finding-id>.diff
  - YAML front-matter per pending-fix.schema.json
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
REMEDIATE_SKILL = SKILLS_DIR / "remediate" / "SKILL.md"


class TestRemediateStateFiles(unittest.TestCase):

    def setUp(self):
        self.assertTrue(REMEDIATE_SKILL.exists())
        self.content = REMEDIATE_SKILL.read_text(encoding="utf-8")
        self.lower = self.content.lower()

    def test_runs_jsonl_declared(self):
        self.assertIn(".vibe-prompt/remediate/state/runs.jsonl", self.content)

    def test_runs_jsonl_is_append_only(self):
        self.assertTrue(
            "append-only" in self.lower or "append only" in self.lower,
            "runs.jsonl must be declared append-only",
        )

    def _entry_shape_section(self) -> str:
        """Return the State files / runs.jsonl entry-shape section."""
        # The dedicated section is "## State files" or the "append-only ledger" sub-section
        state_idx = self.content.find("## State files")
        if state_idx == -1:
            state_idx = self.content.find("append-only ledger")
        if state_idx == -1:
            state_idx = self.content.find("runs.jsonl")
        return self.content[state_idx:state_idx + 4000]

    def test_runs_jsonl_entry_shape_has_timestamp(self):
        self.assertIn("timestamp", self._entry_shape_section())

    def test_runs_jsonl_entry_shape_has_runId(self):
        self.assertIn("runId", self._entry_shape_section())

    def test_runs_jsonl_entry_shape_has_action(self):
        self.assertIn("action", self._entry_shape_section())

    def test_runs_jsonl_entry_shape_has_findingIds(self):
        self.assertIn("findingIds", self._entry_shape_section())

    def test_runs_jsonl_entry_shape_has_confidence(self):
        self.assertIn("confidence", self._entry_shape_section())

    def test_runs_jsonl_entry_shape_has_fileTouched(self):
        self.assertIn("fileTouched", self._entry_shape_section())

    def test_runs_jsonl_entry_shape_has_backupPath(self):
        self.assertIn("backupPath", self._entry_shape_section())

    def test_backup_dir_iso_timestamp_format(self):
        # .vibe-prompt/remediate/backup/<ISO-timestamp>/
        self.assertIn(".vibe-prompt/remediate/backup", self.content)
        # Should mention ISO timestamp format
        self.assertTrue(
            "ISO" in self.content or "YYYY-MM-DD" in self.content,
            "Backup dir naming must declare ISO/YYYY-MM-DD timestamp format",
        )

    def test_pending_dir_layout(self):
        # .vibe-prompt/remediate/pending/<finding-id>.diff
        self.assertIn(".vibe-prompt/remediate/pending", self.content)
        self.assertIn(".diff", self.content)

    def test_pending_front_matter_yaml(self):
        # YAML front-matter format with findingId, findingCategory, confidence
        self.assertTrue(
            "findingId" in self.content
            and "findingCategory" in self.content
            and "confidence" in self.content,
            "Pending file front-matter must declare YAML keys",
        )

    def test_pending_front_matter_references_schema(self):
        # Front-matter validates against pending-fix.schema.json
        self.assertIn("pending-fix.schema.json", self.content)


if __name__ == "__main__":
    unittest.main()
