"""
Task 10 (v0.7) — TDD tests for scan workspace-detection logic in SKILL.md.

Per the plan, fixtures are described in the test as documented detection
behavior — scan/SKILL.md must declare the workspace-detection step before
inventory emission, and the four detection rules (npm-workspaces /
nested-projects / single-workspace / unknown) must be documented.

Asserts (doc-based, matching the project's testing convention):

  Fixture A: top-level package.json with `workspaces: ["packages/*", "apps/*"]`
    → emits `workspaceKind: "npm-workspaces"` with glob expansion documented.
  Fixture B: no top-level package.json but ≥2 nested package.json files
    → emits `workspaceKind: "nested-projects"` with detected nested roots.
  Fixture C: single package.json, no workspaces declaration
    → emits `workspaceKind: "single-workspace"`.
  Fixture D: no package.json at all
    → emits `workspaceKind: "unknown"`.
  Scan SKILL.md must reference config.scan.workspaceDetection for forcing.
  Workspace-detection step runs BEFORE inventory emission.
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
SCAN_SKILL = SKILLS_DIR / "scan" / "SKILL.md"
WORKSPACE_REF = SKILLS_DIR / "scan" / "references" / "workspace-detection.md"


class TestScanWorkspaceDetection(unittest.TestCase):
    def setUp(self):
        self.skill = SCAN_SKILL.read_text(encoding="utf-8")
        self.ref = WORKSPACE_REF.read_text(encoding="utf-8")
        self.combined = self.skill + "\n" + self.ref

    def test_skill_references_workspace_detection_step(self):
        """scan/SKILL.md must declare a workspace-detection step."""
        skill_lower = self.skill.lower()
        self.assertIn(
            "workspace",
            skill_lower,
            "scan/SKILL.md must reference workspace detection",
        )
        # Must point at the reference file for the detection rules
        self.assertIn(
            "workspace-detection.md",
            self.skill,
            "scan/SKILL.md must link to references/workspace-detection.md",
        )

    def test_skill_declares_workspaceKind_emission(self):
        """SKILL.md workflow must declare workspaceKind emission."""
        self.assertIn(
            "workspaceKind",
            self.skill,
            "scan/SKILL.md must declare workspaceKind emission",
        )

    def test_fixture_a_npm_workspaces_rule(self):
        """Fixture A: package.json with workspaces field → npm-workspaces."""
        # Detection rule must be documented in the reference
        self.assertIn(
            "npm-workspaces",
            self.combined,
            "must document npm-workspaces detection rule",
        )
        # Glob expansion must be documented (packages/*, apps/*)
        self.assertIn(
            "packages/*",
            self.combined,
            "must document workspace glob expansion (e.g., packages/*)",
        )

    def test_fixture_b_nested_projects_rule(self):
        """Fixture B: nested package.json without workspaces → nested-projects."""
        self.assertIn(
            "nested-projects",
            self.combined,
            "must document nested-projects detection rule",
        )

    def test_fixture_c_single_workspace_rule(self):
        """Fixture C: single package.json, no workspaces → single-workspace."""
        self.assertIn(
            "single-workspace",
            self.combined,
            "must document single-workspace detection rule",
        )

    def test_fixture_d_unknown_rule(self):
        """Fixture D: no package.json → unknown."""
        # Reference must mention unknown as the no-package-json fallback
        self.assertIn(
            "unknown",
            self.combined,
            "must document unknown workspaceKind (no package.json)",
        )
        ref_lower = self.ref.lower()
        # And the trigger condition must be described
        self.assertIn(
            "no `package.json`",
            self.ref,
            "must document 'no package.json' as the unknown trigger",
        )

    def test_workspace_detection_step_runs_before_inventory_emission(self):
        """SKILL.md workflow must place workspace detection before inventory emission."""
        # Find index of workspace step and inventory emission step
        skill_lower = self.skill.lower()
        workspace_idx = skill_lower.find("workspace")
        inventory_write_idx = skill_lower.find("write inventory")
        self.assertGreaterEqual(
            workspace_idx,
            0,
            "scan/SKILL.md must mention workspace detection",
        )
        self.assertGreaterEqual(
            inventory_write_idx,
            0,
            "scan/SKILL.md must declare an inventory write step",
        )
        self.assertLess(
            workspace_idx,
            inventory_write_idx,
            "workspace detection must run BEFORE inventory write",
        )

    def test_config_workspace_detection_force_documented(self):
        """SKILL.md or reference must document config.scan.workspaceDetection."""
        has_config = (
            "workspaceDetection" in self.combined
            or "force-single" in self.combined
            or "force-monorepo" in self.combined
        )
        self.assertTrue(
            has_config,
            "must document config.scan.workspaceDetection for forcing",
        )


if __name__ == "__main__":
    unittest.main()
