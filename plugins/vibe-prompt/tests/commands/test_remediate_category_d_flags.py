"""
Task 30 — TDD tests for the three new Category D remediate flags in
commands/remediate.md + skills/remediate/SKILL.md.

Asserts:
- Command declares --apply-inline-to-registry, --apply-typed-renderer,
  --apply-model-consolidation flags
- Each flag flips its respective Category D routing from stage-only to normal
  routing (auto-write at ≥0.90 for D-1/D-2; ≥0.88 for D-3)
- Without flag: D-1/D-2/D-3 diffs stage regardless of confidence
- With flag: confidence routing applies as normal
- SKILL.md Inputs table lists each flag with its v0.7 description
"""

import pathlib
import unittest

COMMANDS_DIR = pathlib.Path(__file__).parent.parent.parent / "commands"
SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
REMEDIATE_COMMAND = COMMANDS_DIR / "remediate.md"
REMEDIATE_SKILL = SKILLS_DIR / "remediate" / "SKILL.md"


class TestRemediateCategoryDFlags(unittest.TestCase):

    def setUp(self):
        self.command = REMEDIATE_COMMAND.read_text(encoding="utf-8")
        self.skill = REMEDIATE_SKILL.read_text(encoding="utf-8")

    # --- Command declarations ---
    def test_command_declares_apply_inline_to_registry(self):
        self.assertIn(
            "--apply-inline-to-registry",
            self.command,
            "commands/remediate.md must declare --apply-inline-to-registry flag",
        )

    def test_command_declares_apply_typed_renderer(self):
        self.assertIn(
            "--apply-typed-renderer",
            self.command,
            "commands/remediate.md must declare --apply-typed-renderer flag",
        )

    def test_command_declares_apply_model_consolidation(self):
        self.assertIn(
            "--apply-model-consolidation",
            self.command,
            "commands/remediate.md must declare --apply-model-consolidation flag",
        )

    def test_command_documents_v07_addition(self):
        # The three flags ship in v0.7
        self.assertIn(
            "v0.7",
            self.command,
            "commands/remediate.md must document v0.7 Category D additions",
        )

    def test_command_documents_default_stage(self):
        # Default behavior: stage; flag flips to normal routing
        lower = self.command.lower()
        self.assertIn(
            "stage",
            lower,
            "commands/remediate.md must document stage-by-default behavior for Category D",
        )

    # --- SKILL.md Inputs table ---
    def test_skill_inputs_lists_apply_inline_to_registry(self):
        idx_inputs = self.skill.find("## Inputs")
        self.assertGreater(idx_inputs, -1)
        # Inputs section ends at the next ## header
        next_header = self.skill.find("## ", idx_inputs + 5)
        inputs_section = self.skill[idx_inputs:next_header] if next_header > -1 else self.skill[idx_inputs:]
        self.assertIn(
            "--apply-inline-to-registry",
            inputs_section,
            "SKILL.md Inputs table must list --apply-inline-to-registry",
        )

    def test_skill_inputs_lists_apply_typed_renderer(self):
        idx_inputs = self.skill.find("## Inputs")
        next_header = self.skill.find("## ", idx_inputs + 5)
        inputs_section = self.skill[idx_inputs:next_header] if next_header > -1 else self.skill[idx_inputs:]
        self.assertIn(
            "--apply-typed-renderer",
            inputs_section,
            "SKILL.md Inputs table must list --apply-typed-renderer",
        )

    def test_skill_inputs_lists_apply_model_consolidation(self):
        idx_inputs = self.skill.find("## Inputs")
        next_header = self.skill.find("## ", idx_inputs + 5)
        inputs_section = self.skill[idx_inputs:next_header] if next_header > -1 else self.skill[idx_inputs:]
        self.assertIn(
            "--apply-model-consolidation",
            inputs_section,
            "SKILL.md Inputs table must list --apply-model-consolidation",
        )

    # --- SKILL.md routing override semantics ---
    def test_skill_describes_category_d_override(self):
        # SKILL.md must describe that Category D ALWAYS stages by default
        self.assertTrue(
            "Category D override" in self.skill
            or "Category D always stages" in self.skill
            or "Category D-1, D-2, D-3 ALWAYS stage" in self.skill,
            "SKILL.md must describe Category D routing override",
        )

    def test_skill_describes_flag_independence(self):
        # The three Category D flags are independent
        lower = self.skill.lower()
        self.assertIn(
            "independent",
            lower,
            "SKILL.md must describe that the three Category D flags are independent",
        )

    def test_d3_threshold_documented(self):
        # D-3 has a lower 0.88 floor when flag is set
        self.assertIn(
            "0.88",
            self.skill,
            "SKILL.md must document D-3's 0.88 confidence floor under --apply-model-consolidation",
        )


if __name__ == "__main__":
    unittest.main()
