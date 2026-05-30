"""
Task 19 — TDD tests for --auto-handoff-vibe-sec flag in commands/remediate.md
+ SKILL.md.

Asserts:
- Command declares --auto-handoff-vibe-sec flag
- Default behavior unchanged when flag absent (v0.5 banner-only handoff)
- When flag set + F12 critical fires, SKILL.md workflow includes vibe-sec
  invocation step
"""

import pathlib
import unittest

COMMANDS_DIR = pathlib.Path(__file__).parent.parent.parent / "commands"
SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
REMEDIATE_COMMAND = COMMANDS_DIR / "remediate.md"
REMEDIATE_SKILL = SKILLS_DIR / "remediate" / "SKILL.md"


class TestAutoHandoffVibeSecFlag(unittest.TestCase):

    def setUp(self):
        self.command = REMEDIATE_COMMAND.read_text(encoding="utf-8")
        self.skill = REMEDIATE_SKILL.read_text(encoding="utf-8")

    # --- Command declaration ---
    def test_command_declares_flag(self):
        self.assertIn(
            "--auto-handoff-vibe-sec",
            self.command,
            "commands/remediate.md must declare --auto-handoff-vibe-sec flag",
        )

    def test_command_documents_default_off(self):
        # Default false; opt-in only
        lower = self.command.lower()
        # Either explicit "default" or "opt-in" or "banner-only" semantics
        self.assertTrue(
            "default" in lower
            or "opt-in" in lower
            or "opt in" in lower
            or "banner" in lower,
            "commands/remediate.md must document the default-off / opt-in behavior",
        )

    # --- SKILL.md updates ---
    def test_skill_inputs_table_lists_auto_handoff_flag(self):
        idx_inputs = self.skill.find("## Inputs")
        self.assertGreater(idx_inputs, -1, "SKILL.md must have Inputs section")
        next_section_idx = self.skill.find("## ", idx_inputs + 10)
        inputs_section = self.skill[idx_inputs:next_section_idx]
        self.assertIn(
            "--auto-handoff-vibe-sec",
            inputs_section,
            "Inputs table must list --auto-handoff-vibe-sec",
        )

    def test_skill_documents_default_banner_only(self):
        lower = self.skill.lower()
        # The v0.5 banner-only behavior is preserved as default
        self.assertTrue(
            "banner-only" in lower
            or "banner only" in lower
            or "v0.5 banner" in lower
            or "default is the v0.5" in lower,
            "SKILL.md must document the v0.5 banner-only default",
        )

    def test_skill_documents_f12_critical_triggers_workflow(self):
        # When flag set + F12 critical fires, workflow includes vibe-sec invocation
        idx = self.skill.find("--auto-handoff-vibe-sec")
        self.assertGreater(idx, -1, "SKILL.md must reference --auto-handoff-vibe-sec")
        section = self.skill[max(0, idx - 200):idx + 2500].lower()
        # F12 critical must be the trigger
        self.assertIn(
            "f12",
            section,
            "SKILL.md must wire --auto-handoff-vibe-sec to F12 critical findings",
        )

    def test_skill_documents_vibe_sec_invocation_step(self):
        # SKILL.md workflow must include vibe-sec invocation step
        lower = self.skill.lower()
        self.assertTrue(
            "vibe-sec" in lower,
            "SKILL.md must reference vibe-sec invocation",
        )


if __name__ == "__main__":
    unittest.main()
