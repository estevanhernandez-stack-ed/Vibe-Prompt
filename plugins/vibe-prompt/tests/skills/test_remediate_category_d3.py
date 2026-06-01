"""
Task 27 — TDD tests for Category D-3 (model-consolidation) migration template
declared in fix-categories.md + driven by remediate/SKILL.md.

Asserts:
- fix-categories.md declares Category D-3 with target finding F6
- Confidence default is 0.88
- Routing default is auto-write at top end (≥0.88 with flag)
- migrationKind = "D-3-model-consolidation"; findingCategory = "D-3"
- remediate/SKILL.md describes D-3 generation step including DEFAULT_MODEL
- Monorepo handling: per-workspace config files when models differ across workspaces
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
FIX_CATEGORIES = SKILLS_DIR / "remediate" / "references" / "fix-categories.md"
REMEDIATE_SKILL = SKILLS_DIR / "remediate" / "SKILL.md"


class TestCategoryD3ModelConsolidation(unittest.TestCase):

    def setUp(self):
        self.fix_categories = FIX_CATEGORIES.read_text(encoding="utf-8")
        self.skill = REMEDIATE_SKILL.read_text(encoding="utf-8")

    # --- fix-categories.md declarations ---
    def test_category_d3_declared(self):
        self.assertIn(
            "D-3",
            self.fix_categories,
            "fix-categories.md must declare Category D-3 sub-category",
        )

    def test_d3_targets_f6(self):
        idx = self.fix_categories.find("D-3")
        self.assertGreater(idx, -1)
        section = self.fix_categories[idx:idx + 2500]
        self.assertIn("F6", section, "Category D-3 must reference F6 finding")

    def test_d3_confidence_0_88(self):
        idx = self.fix_categories.find("D-3")
        section = self.fix_categories[idx:idx + 2500]
        self.assertIn(
            "0.88",
            section,
            "Category D-3 must declare 0.88 default confidence",
        )

    def test_d3_routing_default_auto_write(self):
        idx = self.fix_categories.find("D-3")
        section = self.fix_categories[idx:idx + 2500].lower()
        self.assertTrue(
            "auto-write" in section or "auto write" in section,
            "Category D-3 routing default is auto-write at top end",
        )

    def test_d3_apply_flag_declared(self):
        idx = self.fix_categories.find("D-3")
        section = self.fix_categories[idx:idx + 2500]
        self.assertIn(
            "--apply-model-consolidation",
            section,
            "Category D-3 must reference --apply-model-consolidation opt-in flag",
        )

    def test_d3_migration_kind_documented(self):
        idx = self.fix_categories.find("D-3")
        section = self.fix_categories[idx:idx + 2500]
        self.assertIn(
            "D-3-model-consolidation",
            section,
            "Category D-3 must declare migrationKind = D-3-model-consolidation",
        )

    def test_d3_voice_risk_1_0(self):
        idx = self.fix_categories.find("D-3")
        section = self.fix_categories[idx:idx + 2500]
        # voice-risk is 1.0 because model IDs are pure config
        self.assertIn(
            "1.0",
            section,
            "Category D-3 must declare voice-risk 1.0 (model IDs are pure config)",
        )

    def test_d3_monorepo_handling(self):
        idx = self.fix_categories.find("D-3")
        section = self.fix_categories[idx:idx + 2500].lower()
        # Per-workspace config when models differ across workspaces
        self.assertTrue(
            "monorepo" in section or "workspace" in section,
            "Category D-3 must document monorepo per-workspace handling",
        )

    # --- remediate/SKILL.md instructions ---
    def test_skill_describes_d3_model_consolidation(self):
        self.assertIn(
            "D-3",
            self.skill,
            "remediate SKILL.md must describe D-3 model-consolidation generation",
        )

    def test_skill_references_apply_model_consolidation_flag(self):
        self.assertIn(
            "--apply-model-consolidation",
            self.skill,
            "remediate SKILL.md must reference --apply-model-consolidation flag",
        )

    def test_skill_describes_default_model_export(self):
        self.assertIn(
            "DEFAULT_MODEL",
            self.skill,
            "remediate SKILL.md must describe DEFAULT_MODEL export generation",
        )

    def test_skill_describes_per_workspace_config_for_monorepo(self):
        idx = self.skill.find("D-3")
        section = self.skill[idx:idx + 3000].lower()
        self.assertTrue(
            "monorepo" in section or "workspace" in section,
            "remediate SKILL.md must describe per-workspace config for monorepos",
        )

    def test_skill_describes_threshold_n_3(self):
        # Threshold: N ≥ 3 to fire D-3
        idx = self.skill.find("D-3")
        section = self.skill[idx:idx + 3000]
        self.assertTrue(
            "N=3" in section or "N≥3" in section or "N >= 3" in section or "N ≥ 3" in section,
            "remediate SKILL.md must declare D-3 firing threshold (N ≥ 3 occurrences)",
        )


if __name__ == "__main__":
    unittest.main()
