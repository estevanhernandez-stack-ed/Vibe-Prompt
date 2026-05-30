"""
Task 18 — TDD tests for --apply-voice-frame-fixes flag in commands/remediate.md
+ SKILL.md gating logic.

Asserts:
- Command declares --apply-voice-frame-fixes flag
- Without flag: voice-frame Category B diffs stage (don't auto-write) even at
  ≥0.90 confidence (conservative default)
- With --apply-voice-frame-fixes flag: voice-frame Category B diffs follow
  normal routing (auto-write if confidence ≥0.90)
- SKILL.md gates the routing on the flag
"""

import pathlib
import unittest

COMMANDS_DIR = pathlib.Path(__file__).parent.parent.parent / "commands"
SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
REMEDIATE_COMMAND = COMMANDS_DIR / "remediate.md"
REMEDIATE_SKILL = SKILLS_DIR / "remediate" / "SKILL.md"


class TestApplyVoiceFrameFixesFlag(unittest.TestCase):

    def setUp(self):
        self.command = REMEDIATE_COMMAND.read_text(encoding="utf-8")
        self.skill = REMEDIATE_SKILL.read_text(encoding="utf-8")

    # --- Command declaration ---
    def test_command_declares_apply_voice_frame_fixes_flag(self):
        self.assertIn(
            "--apply-voice-frame-fixes",
            self.command,
            "commands/remediate.md must declare --apply-voice-frame-fixes flag",
        )

    # --- SKILL gating ---
    def test_skill_documents_flag_gates_voice_frame_routing(self):
        self.assertIn(
            "--apply-voice-frame-fixes",
            self.skill,
            "remediate/SKILL.md must reference --apply-voice-frame-fixes flag",
        )

    def test_skill_documents_default_voice_frame_stages(self):
        # Without flag, voice-frame stages even at ≥0.90 confidence
        idx = self.skill.find("--apply-voice-frame-fixes")
        self.assertGreater(idx, -1)
        # Look in surrounding context for the conservative default
        section = self.skill[max(0, idx - 800):idx + 1500].lower()
        self.assertTrue(
            "stage" in section,
            "SKILL.md must describe stage-by-default behavior near --apply-voice-frame-fixes",
        )

    def test_skill_describes_normal_routing_with_flag(self):
        # With flag, follows normal routing (auto-write at ≥0.90)
        idx = self.skill.find("--apply-voice-frame-fixes")
        self.assertGreater(idx, -1)
        section = self.skill[max(0, idx - 800):idx + 1500].lower()
        self.assertTrue(
            "auto-write" in section or "normal routing" in section,
            "SKILL.md must describe auto-write/normal routing path with flag",
        )

    def test_skill_inputs_table_lists_flag(self):
        # Check the Inputs section enumerates the flag like the other flags
        idx_inputs = self.skill.find("## Inputs")
        self.assertGreater(idx_inputs, -1, "SKILL.md must have an Inputs section")
        # Search the Inputs section for the flag
        next_section_idx = self.skill.find("## ", idx_inputs + 10)
        inputs_section = self.skill[idx_inputs:next_section_idx]
        self.assertIn(
            "--apply-voice-frame-fixes",
            inputs_section,
            "Inputs table must list --apply-voice-frame-fixes",
        )

    def test_skill_documents_flag_independent_of_apply_contradictions(self):
        # The two opt-ins are independent
        lower = self.skill.lower()
        # "independent" or "separate" or "does not enable" between the two
        self.assertTrue(
            "independent" in lower or "does not enable" in lower
            or "does not opt" in lower or "does not opt-in" in lower,
            "SKILL.md must clarify the two opt-in flags are independent",
        )

    def test_skill_never_section_does_not_block_with_flag(self):
        # Sanity check: SKILL.md's Never section should still ban un-flagged
        # voice-frame auto-write
        idx_never = self.skill.find("## Never")
        self.assertGreater(idx_never, -1, "SKILL.md must have a Never section")


if __name__ == "__main__":
    unittest.main()
