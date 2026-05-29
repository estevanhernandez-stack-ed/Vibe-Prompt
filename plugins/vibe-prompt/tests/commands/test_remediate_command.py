"""
Task 21 — TDD tests for commands/remediate.md.

Asserts the command file exists, declares /vibe-prompt:remediate, and documents
all 7 flags per spec §"Command additions".
"""

import pathlib
import unittest

COMMANDS_DIR = pathlib.Path(__file__).parent.parent.parent / "commands"
REMEDIATE_COMMAND = COMMANDS_DIR / "remediate.md"


class TestRemediateCommand(unittest.TestCase):

    def setUp(self):
        self.assertTrue(
            REMEDIATE_COMMAND.exists(),
            f"commands/remediate.md must exist at {REMEDIATE_COMMAND}",
        )
        self.content = REMEDIATE_COMMAND.read_text(encoding="utf-8")

    def test_has_frontmatter(self):
        self.assertTrue(
            self.content.startswith("---"),
            "commands/remediate.md must start with YAML front-matter",
        )

    def test_has_description(self):
        self.assertIn(
            "description:",
            self.content,
            "Front-matter must include description",
        )

    def test_invokes_remediate_skill(self):
        # Command should invoke the vibe-prompt:remediate skill
        self.assertIn(
            "vibe-prompt:remediate",
            self.content,
            "Command must invoke the vibe-prompt:remediate skill",
        )

    # Seven flags
    def test_flag_apply_pending(self):
        self.assertIn("--apply-pending", self.content)

    def test_flag_reject_pending(self):
        self.assertIn("--reject-pending", self.content)

    def test_flag_rollback(self):
        self.assertIn("--rollback", self.content)

    def test_flag_interactive(self):
        self.assertIn("--interactive", self.content)

    def test_flag_auto_apply(self):
        self.assertIn("--auto-apply", self.content)

    def test_flag_skip_f12(self):
        self.assertIn("--skip-f12", self.content)

    def test_flag_apply_contradictions(self):
        self.assertIn("--apply-contradictions", self.content)


if __name__ == "__main__":
    unittest.main()
