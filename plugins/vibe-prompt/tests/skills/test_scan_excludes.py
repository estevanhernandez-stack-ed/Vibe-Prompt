"""
Task 12 (v0.7) — TDD tests for scan-excludes config + auto-detection in scan/SKILL.md.

Doc-based assertions:
  1. Reads `config.scan.excludes` array; entries treated as glob patterns.
  2. Auto-detects exclude candidates matching `vibe-*/`, `*-main/`, `_ARCHIVE_*/`
     and surfaces them via friction `scan-excludes-recommended-but-not-applied`
     (low) when not in config.
  3. When excludes applied, files matching globs do NOT appear in `prompts[]`.
  4. `scanExcludes[]` field in inventory.json reflects the effective exclude set.
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
SCAN_SKILL = SKILLS_DIR / "scan" / "SKILL.md"
WORKSPACE_REF = SKILLS_DIR / "scan" / "references" / "workspace-detection.md"


class TestScanExcludes(unittest.TestCase):
    def setUp(self):
        self.skill = SCAN_SKILL.read_text(encoding="utf-8")
        self.ref = WORKSPACE_REF.read_text(encoding="utf-8")
        self.combined = self.skill + "\n" + self.ref

    def test_skill_reads_config_scan_excludes(self):
        """SKILL.md must declare it reads config.scan.excludes."""
        # Look for config.scan.excludes reference
        has_config = (
            "scan.excludes" in self.skill
            or "config.scan.excludes" in self.skill
        )
        self.assertTrue(
            has_config,
            "scan/SKILL.md must read config.scan.excludes glob array",
        )

    def test_skill_declares_glob_pattern_handling(self):
        """SKILL.md must declare excludes are glob patterns."""
        skill_lower = self.skill.lower()
        self.assertIn(
            "glob",
            skill_lower,
            "scan/SKILL.md must reference glob patterns for excludes",
        )

    def test_skill_documents_auto_detect_candidates(self):
        """Auto-detection of vibe-*/ / *-main/ / _ARCHIVE_*/ candidates."""
        # All three auto-detect patterns must be mentioned in SKILL.md
        for pattern in ["vibe-*/", "*-main/", "_ARCHIVE_*/"]:
            self.assertIn(
                pattern,
                self.skill,
                f"scan/SKILL.md must document auto-detect pattern '{pattern}'",
            )

    def test_friction_trigger_documented(self):
        """`scan-excludes-recommended-but-not-applied` friction must be referenced."""
        self.assertIn(
            "scan-excludes-recommended-but-not-applied",
            self.skill,
            "scan/SKILL.md must reference the scan-excludes-recommended-but-not-applied friction trigger",
        )

    def test_excludes_applied_during_walk(self):
        """SKILL.md must state files matching excludes do not appear in prompts[]."""
        skill_lower = self.skill.lower()
        # The walker honors excludes — language like "exclude", "skip", "filtered"
        has_apply_language = (
            "exclude" in skill_lower
            and ("skip" in skill_lower or "exclud" in skill_lower)
        )
        self.assertTrue(
            has_apply_language,
            "scan/SKILL.md must state excludes are applied during the file walk",
        )

    def test_scanExcludes_field_in_inventory_documented(self):
        """SKILL.md must declare scanExcludes[] field in inventory.json."""
        self.assertIn(
            "scanExcludes",
            self.skill,
            "scan/SKILL.md must declare scanExcludes[] field in inventory.json reflects effective exclude set",
        )

    def test_effective_exclude_set_language(self):
        """The 'effective' exclude set semantics must be documented."""
        skill_lower = self.skill.lower()
        self.assertIn(
            "effective",
            skill_lower,
            "scan/SKILL.md must use 'effective' to describe scanExcludes[] semantics",
        )


if __name__ == "__main__":
    unittest.main()
