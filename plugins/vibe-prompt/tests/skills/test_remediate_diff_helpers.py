"""
Task 19 — TDD tests for skills/remediate/references/diff-patch-helpers.md.

Asserts the file declares unified-diff format, patch algorithm, conflict detection,
and recovery rules.
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
HELPERS = SKILLS_DIR / "remediate" / "references" / "diff-patch-helpers.md"


class TestRemediateDiffHelpers(unittest.TestCase):

    def setUp(self):
        self.assertTrue(
            HELPERS.exists(),
            f"references/diff-patch-helpers.md must exist at {HELPERS}",
        )
        self.content = HELPERS.read_text(encoding="utf-8")
        self.lower = self.content.lower()

    def test_unified_diff_format_referenced(self):
        self.assertTrue(
            "unified diff" in self.lower or "unified-diff" in self.lower,
            "Must reference unified diff format",
        )
        # @@ hunk markers
        self.assertIn("@@", self.content, "Must show @@ hunk markers")

    def test_patch_algorithm_described(self):
        # Line-context match + apply
        lower = self.lower
        self.assertTrue(
            "context" in lower and ("match" in lower or "apply" in lower),
            "Must describe line-context match + apply algorithm",
        )

    def test_conflict_detection_described(self):
        lower = self.lower
        self.assertTrue(
            "conflict" in lower,
            "Must describe conflict detection",
        )
        # Drift since audit
        self.assertTrue(
            "drift" in lower or "changed" in lower or "stale" in lower,
            "Must mention drift/staleness as conflict trigger",
        )

    def test_recovery_skip_friction_log(self):
        lower = self.lower
        self.assertTrue(
            "skip" in lower,
            "Recovery must declare skip behavior on conflict",
        )
        self.assertTrue(
            "friction-log" in lower or "friction log" in lower,
            "Recovery must log to friction on conflict",
        )

    def test_friction_trigger_named(self):
        # The conflict friction trigger should be named
        self.assertTrue(
            "auto-write-conflict" in self.content or "diff-conflict" in self.content
            or "patch-conflict" in self.content,
            "Must name a friction trigger for conflicts (e.g., auto-write-conflict)",
        )


if __name__ == "__main__":
    unittest.main()
