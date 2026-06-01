"""
Task 25 — TDD tests for Category D-1 (inline-to-registry) migration template
declared in fix-categories.md + driven by remediate/SKILL.md.

Asserts:
- fix-categories.md declares Category D-1 with target finding F1
- Confidence default is 0.85
- Routing default is stage; --apply-inline-to-registry flag unlocks auto-write at ≥0.90
- migrationKind = "D-1-inline-to-registry"; findingCategory = "D-1"
- remediate/SKILL.md describes the Category D-1 generation step
- Per-call-site independence — multiple inline sites can be migrated independently
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
FIX_CATEGORIES = SKILLS_DIR / "remediate" / "references" / "fix-categories.md"
REMEDIATE_SKILL = SKILLS_DIR / "remediate" / "SKILL.md"


class TestCategoryD1InlineToRegistry(unittest.TestCase):

    def setUp(self):
        self.fix_categories = FIX_CATEGORIES.read_text(encoding="utf-8")
        self.skill = REMEDIATE_SKILL.read_text(encoding="utf-8")

    # --- fix-categories.md declarations ---
    def test_category_d_declared(self):
        self.assertIn(
            "Category D",
            self.fix_categories,
            "fix-categories.md must declare Category D for v0.7 migration templates",
        )

    def test_category_d1_declared(self):
        self.assertIn(
            "D-1",
            self.fix_categories,
            "fix-categories.md must declare Category D-1 sub-category",
        )

    def test_d1_targets_f1(self):
        idx = self.fix_categories.find("D-1")
        self.assertGreater(idx, -1)
        section = self.fix_categories[idx:idx + 2500]
        self.assertIn("F1", section, "Category D-1 must reference F1 finding")

    def test_d1_confidence_0_85(self):
        idx = self.fix_categories.find("D-1")
        section = self.fix_categories[idx:idx + 2500]
        self.assertIn(
            "0.85",
            section,
            "Category D-1 must declare 0.85 default confidence",
        )

    def test_d1_routing_default_stage(self):
        idx = self.fix_categories.find("D-1")
        section = self.fix_categories[idx:idx + 2500].lower()
        self.assertIn(
            "stage",
            section,
            "Category D-1 routing default is stage",
        )

    def test_d1_apply_flag_declared(self):
        idx = self.fix_categories.find("D-1")
        section = self.fix_categories[idx:idx + 2500]
        self.assertIn(
            "--apply-inline-to-registry",
            section,
            "Category D-1 must reference --apply-inline-to-registry opt-in flag",
        )

    def test_d1_migration_kind_documented(self):
        idx = self.fix_categories.find("D-1")
        section = self.fix_categories[idx:idx + 2500]
        self.assertIn(
            "D-1-inline-to-registry",
            section,
            "Category D-1 must declare migrationKind = D-1-inline-to-registry",
        )

    # --- remediate/SKILL.md instructions ---
    def test_skill_describes_category_d_generation(self):
        self.assertIn(
            "Category D",
            self.skill,
            "remediate SKILL.md must describe Category D generation",
        )

    def test_skill_describes_d1_inline_to_registry(self):
        self.assertIn(
            "D-1",
            self.skill,
            "remediate SKILL.md must describe D-1 inline-to-registry generation",
        )

    def test_skill_references_apply_inline_to_registry_flag(self):
        self.assertIn(
            "--apply-inline-to-registry",
            self.skill,
            "remediate SKILL.md must reference --apply-inline-to-registry flag",
        )

    def test_skill_describes_per_call_site_independence(self):
        # Multiple D-1 diffs may exist for same finding-id list
        idx = self.skill.find("D-1")
        section = self.skill[idx:idx + 3000].lower()
        self.assertTrue(
            "per-call-site" in section or "per call site" in section or "independently" in section,
            "Category D-1 must describe per-call-site independence",
        )

    def test_skill_references_migration_templates(self):
        # SKILL.md should load migration-templates.md
        self.assertIn(
            "migration-templates.md",
            self.skill,
            "remediate SKILL.md must reference migration-templates.md",
        )


if __name__ == "__main__":
    unittest.main()
