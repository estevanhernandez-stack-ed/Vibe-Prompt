"""
Task 8 (v0.7) — TDD tests for workspace-detection.md reference.

Asserts:
  1. File exists at skills/scan/references/workspace-detection.md
  2. Contains required sections:
     - "npm workspaces detection"
     - "Nested package.json detection (no `workspaces` declaration)"
     - "Exclude defaults"
     - "Confidence calibration"
  3. Documents the four workspaceKind enum values
  4. Includes default exclude glob list:
     vibe-*/, *-main/, _ARCHIVE_*/, node_modules/, .git/, dist/, build/
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
WORKSPACE_REF = SKILLS_DIR / "scan" / "references" / "workspace-detection.md"


class TestWorkspaceDetectionReference(unittest.TestCase):
    def setUp(self):
        self.path = WORKSPACE_REF

    def test_file_exists(self):
        self.assertTrue(
            self.path.exists(),
            f"workspace-detection.md must exist at {self.path}",
        )

    def test_contains_npm_workspaces_section(self):
        content = self.path.read_text(encoding="utf-8")
        self.assertIn(
            "npm workspaces detection",
            content,
            "must contain 'npm workspaces detection' section",
        )

    def test_contains_nested_package_json_section(self):
        content = self.path.read_text(encoding="utf-8")
        self.assertIn(
            "Nested package.json detection",
            content,
            "must contain 'Nested package.json detection' section",
        )
        self.assertIn(
            "no `workspaces` declaration",
            content,
            "nested section header must clarify no workspaces declaration",
        )

    def test_contains_exclude_defaults_section(self):
        content = self.path.read_text(encoding="utf-8")
        self.assertIn(
            "Exclude defaults",
            content,
            "must contain 'Exclude defaults' section",
        )

    def test_contains_confidence_calibration_section(self):
        content = self.path.read_text(encoding="utf-8")
        self.assertIn(
            "Confidence calibration",
            content,
            "must contain 'Confidence calibration' section",
        )

    def test_documents_four_workspace_kinds(self):
        content = self.path.read_text(encoding="utf-8")
        for kind in [
            "single-workspace",
            "npm-workspaces",
            "nested-projects",
            "unknown",
        ]:
            self.assertIn(
                kind,
                content,
                f"must document workspaceKind value '{kind}'",
            )

    def test_default_exclude_globs_documented(self):
        content = self.path.read_text(encoding="utf-8")
        for glob in [
            "vibe-*/",
            "*-main/",
            "_ARCHIVE_*/",
            "node_modules/",
            ".git/",
            "dist/",
            "build/",
        ]:
            self.assertIn(
                glob,
                content,
                f"must include default exclude glob '{glob}'",
            )


if __name__ == "__main__":
    unittest.main()
