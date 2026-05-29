"""
Task 20 — TDD tests for skills/remediate/references/rollback-workflow.md.

Asserts rollback behavior: find batch by timestamp, restore each .bak atomically,
log to runs.jsonl, handle missing/partial backups gracefully.
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
ROLLBACK = SKILLS_DIR / "remediate" / "references" / "rollback-workflow.md"


class TestRemediateRollback(unittest.TestCase):

    def setUp(self):
        self.assertTrue(
            ROLLBACK.exists(),
            f"references/rollback-workflow.md must exist at {ROLLBACK}",
        )
        self.content = ROLLBACK.read_text(encoding="utf-8")
        self.lower = self.content.lower()

    def test_finds_backup_batch_by_timestamp(self):
        # ISO-timestamp + backup dir lookup
        self.assertIn(".vibe-prompt/remediate/backup", self.content)
        lower = self.lower
        self.assertTrue(
            "timestamp" in lower,
            "Must reference timestamp lookup for batch",
        )

    def test_restores_bak_files(self):
        self.assertIn(".bak", self.content)
        lower = self.lower
        self.assertTrue(
            "restore" in lower or "rollback" in lower,
            "Must describe restore action",
        )

    def test_atomic_all_or_none(self):
        lower = self.lower
        self.assertTrue(
            "atomic" in lower or "all or none" in lower or "all-or-none" in lower,
            "Must declare atomic / all-or-none semantics",
        )

    def test_logs_to_runs_jsonl(self):
        self.assertIn("runs.jsonl", self.content)
        # action: rolled-back
        self.assertTrue(
            "rolled-back" in self.content or "rollback" in self.lower,
        )

    def test_handles_missing_backup_gracefully(self):
        lower = self.lower
        self.assertTrue(
            "missing" in lower or "absent" in lower or "not found" in lower,
            "Must handle missing-backup case",
        )

    def test_handles_partial_backup_gracefully(self):
        lower = self.lower
        self.assertTrue(
            "partial" in lower or "incomplete" in lower,
            "Must handle partial-backup case",
        )

    def test_friction_log_on_rollback(self):
        # auto-write-rolled-back trigger
        self.assertTrue(
            "auto-write-rolled-back" in self.content
            or "rolled-back" in self.content,
            "Must reference the auto-write-rolled-back friction trigger",
        )


if __name__ == "__main__":
    unittest.main()
