"""
Task 26 — TDD tests for Category D-2 (typed-renderer) migration template
declared in fix-categories.md + driven by remediate/SKILL.md.

Asserts:
- fix-categories.md declares Category D-2 with target finding F4
- Confidence default is 0.75
- Routing default is stage; --apply-typed-renderer flag unlocks auto-write at ≥0.90
- migrationKind = "D-2-typed-renderer"; findingCategory = "D-2"
- remediate/SKILL.md describes the Category D-2 generation step
- Diff template includes requiredVars + renderPrompt helper
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
FIX_CATEGORIES = SKILLS_DIR / "remediate" / "references" / "fix-categories.md"
REMEDIATE_SKILL = SKILLS_DIR / "remediate" / "SKILL.md"


class TestCategoryD2TypedRenderer(unittest.TestCase):

    def setUp(self):
        self.fix_categories = FIX_CATEGORIES.read_text(encoding="utf-8")
        self.skill = REMEDIATE_SKILL.read_text(encoding="utf-8")

    # --- fix-categories.md declarations ---
    def test_category_d2_declared(self):
        self.assertIn(
            "D-2",
            self.fix_categories,
            "fix-categories.md must declare Category D-2 sub-category",
        )

    def test_d2_targets_f4(self):
        idx = self.fix_categories.find("D-2")
        self.assertGreater(idx, -1)
        section = self.fix_categories[idx:idx + 2500]
        self.assertIn("F4", section, "Category D-2 must reference F4 finding")

    def test_d2_confidence_0_75(self):
        idx = self.fix_categories.find("D-2")
        section = self.fix_categories[idx:idx + 2500]
        self.assertIn(
            "0.75",
            section,
            "Category D-2 must declare 0.75 default confidence",
        )

    def test_d2_routing_default_stage(self):
        idx = self.fix_categories.find("D-2")
        section = self.fix_categories[idx:idx + 2500].lower()
        self.assertIn(
            "stage",
            section,
            "Category D-2 routing default is stage",
        )

    def test_d2_apply_flag_declared(self):
        idx = self.fix_categories.find("D-2")
        section = self.fix_categories[idx:idx + 2500]
        self.assertIn(
            "--apply-typed-renderer",
            section,
            "Category D-2 must reference --apply-typed-renderer opt-in flag",
        )

    def test_d2_migration_kind_documented(self):
        idx = self.fix_categories.find("D-2")
        section = self.fix_categories[idx:idx + 2500]
        self.assertIn(
            "D-2-typed-renderer",
            section,
            "Category D-2 must declare migrationKind = D-2-typed-renderer",
        )

    # --- remediate/SKILL.md instructions ---
    def test_skill_describes_d2_typed_renderer(self):
        self.assertIn(
            "D-2",
            self.skill,
            "remediate SKILL.md must describe D-2 typed-renderer generation",
        )

    def test_skill_references_apply_typed_renderer_flag(self):
        self.assertIn(
            "--apply-typed-renderer",
            self.skill,
            "remediate SKILL.md must reference --apply-typed-renderer flag",
        )

    def test_skill_describes_required_vars_addition(self):
        self.assertIn(
            "requiredVars",
            self.skill,
            "remediate SKILL.md must describe requiredVars interface addition",
        )

    def test_skill_describes_render_prompt_helper(self):
        self.assertIn(
            "renderPrompt",
            self.skill,
            "remediate SKILL.md must describe renderPrompt helper generation",
        )

    def test_skill_describes_call_site_updates(self):
        # SKILL.md should mention updating call sites
        idx = self.skill.find("D-2")
        section = self.skill[idx:idx + 3000].lower()
        self.assertTrue(
            "call site" in section or "call-site" in section or "interpolation" in section,
            "remediate SKILL.md must describe call-site updates for D-2",
        )


if __name__ == "__main__":
    unittest.main()
