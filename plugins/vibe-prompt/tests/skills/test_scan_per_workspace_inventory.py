"""
Task 11 (v0.7) — TDD tests for per-workspace inventory emission in scan/SKILL.md.

Doc-based assertions following the project's testing convention:

Fixture: workspaceKind `npm-workspaces` with 3 workspaces →
  emits 3 files at `.vibe-prompt/state/inventory-<workspace-name>.json`
  PLUS top-level aggregator `.vibe-prompt/state/inventory.json` that
  cross-references each via `workspaces[].inventoryFile`.
  Each per-workspace inventory has its own `prompts[]` array scoped
  to that workspace.
  Top-level aggregator's `prompts[]` is a flat union but each entry
  has `workspaceIdentifier` field added.

Fixture: workspaceKind `single-workspace` → emits only the top-level
  inventory (no per-workspace files), no `workspaces[]` array
  (v0.6 compatible shape).
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
SCAN_SKILL = SKILLS_DIR / "scan" / "SKILL.md"


class TestScanPerWorkspaceInventory(unittest.TestCase):
    def setUp(self):
        self.skill = SCAN_SKILL.read_text(encoding="utf-8")

    def test_per_workspace_inventory_file_pattern_documented(self):
        """SKILL.md must declare per-workspace inventory file naming."""
        self.assertIn(
            "inventory-",
            self.skill,
            "scan/SKILL.md must declare `inventory-<workspace>.json` per-workspace file pattern",
        )

    def test_aggregator_inventory_file_documented(self):
        """SKILL.md must declare top-level inventory.json acts as aggregator."""
        self.assertIn(
            "inventory.json",
            self.skill,
            "scan/SKILL.md must reference top-level inventory.json aggregator",
        )

    def test_aggregator_cross_references_workspaces(self):
        """Aggregator must cross-reference per-workspace files via workspaces[].inventoryFile."""
        skill_lower = self.skill.lower()
        self.assertIn(
            "aggregator",
            skill_lower,
            "scan/SKILL.md must use the word 'aggregator' to describe top-level cross-reference",
        )
        self.assertIn(
            "inventoryFile",
            self.skill,
            "scan/SKILL.md must reference workspaces[].inventoryFile cross-reference field",
        )

    def test_per_workspace_prompts_scoped(self):
        """Per-workspace inventories must scope their own prompts[] array."""
        skill_lower = self.skill.lower()
        # Per-workspace scoping language
        has_scope = (
            "per-workspace" in skill_lower
            or "per workspace" in skill_lower
            or "scoped" in skill_lower
        )
        self.assertTrue(
            has_scope,
            "scan/SKILL.md must declare per-workspace prompt scoping",
        )

    def test_workspaceIdentifier_in_aggregator_entries(self):
        """Top-level aggregator entries must carry workspaceIdentifier."""
        self.assertIn(
            "workspaceIdentifier",
            self.skill,
            "scan/SKILL.md must declare workspaceIdentifier on aggregator entries",
        )

    def test_single_workspace_back_compat_shape(self):
        """workspaceKind single-workspace → flat v0.6 shape, no per-workspace files."""
        skill_lower = self.skill.lower()
        # Must declare the back-compat branch
        has_back_compat = (
            "back-compat" in skill_lower
            or "v0.6" in skill_lower
            or "single-workspace" in skill_lower
        )
        self.assertTrue(
            has_back_compat,
            "scan/SKILL.md must document single-workspace back-compat shape (no per-workspace files)",
        )

    def test_branches_on_workspaceKind(self):
        """Inventory emission must branch on workspaceKind."""
        skill_lower = self.skill.lower()
        # Multiple kinds must be referenced in emission context
        self.assertIn(
            "npm-workspaces",
            self.skill,
            "scan/SKILL.md must reference npm-workspaces emission branch",
        )
        self.assertIn(
            "single-workspace",
            self.skill,
            "scan/SKILL.md must reference single-workspace emission branch",
        )


if __name__ == "__main__":
    unittest.main()
