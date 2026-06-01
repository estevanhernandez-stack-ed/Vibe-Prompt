"""
Task 19 — TDD tests for audit per-composer iteration (v0.7).

v0.6 ran F12 (and other composer-aware findings) once globally — keyed off the
single top-level layers[] in composer.json. v0.7 introduces composers[] as
an array (multi-composer / multi-call-site / shared-package) and the audit
must iterate composer-aware findings ONCE PER composer, emitting
`composerIdentifier` on each finding so the dashboard can attribute
findings back to the right composer.

Back-compat: composer.json with no `composers[]` (v0.6 shape, just top-level
`layers[]`) is treated as a single composer with `composerIdentifier: null`
on emitted findings.

Asserts:
  1. audit/SKILL.md documents per-composer iteration over composers[]
  2. SKILL says F12 (and other composer-aware findings) run once per composer
  3. SKILL emits `composerIdentifier` on findings (matching the composer's path)
  4. SKILL documents the back-compat case: composer.json with no composers[]
     runs as a single composer with composerIdentifier: null
  5. SKILL references v0.7 explicitly for this iteration step
"""

import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent.parent.parent
AUDIT_SKILL = ROOT / "skills" / "audit" / "SKILL.md"


class TestAuditPerComposerIteration(unittest.TestCase):

    def setUp(self):
        self.skill = AUDIT_SKILL.read_text(encoding="utf-8")

    def test_skill_documents_per_composer_iteration(self):
        """audit/SKILL.md must document iteration over composers[] array."""
        has_iteration = (
            "composers[]" in self.skill
            or "composers[" in self.skill
            or "per composer" in self.skill.lower()
            or "per-composer" in self.skill.lower()
        )
        self.assertTrue(
            has_iteration,
            "audit/SKILL.md must document per-composer iteration over composers[]"
        )

    def test_skill_documents_f12_runs_once_per_composer(self):
        """SKILL must document F12 runs once per composer entry."""
        # Find the F12 section or the iteration step
        lowered = self.skill.lower()
        has_once_per = (
            ("once per composer" in lowered)
            or ("iterate" in lowered and "composer" in lowered and "f12" in lowered)
            or ("loop" in lowered and "composer" in lowered)
        )
        self.assertTrue(
            has_once_per,
            "audit/SKILL.md must document F12 (and composer-aware findings) running once per composer"
        )

    def test_skill_emits_composer_identifier(self):
        """Findings must emit composerIdentifier field."""
        self.assertIn(
            "composerIdentifier",
            self.skill,
            "audit/SKILL.md must declare emission of composerIdentifier on composer-aware findings"
        )

    def test_skill_documents_back_compat_no_composers_array(self):
        """SKILL must document the v0.6 back-compat case (composer.json with no composers[]) → composerIdentifier: null."""
        lowered = self.skill.lower()
        has_back_compat = (
            ("composerIdentifier: null" in self.skill)
            or ("composerIdentifier" in self.skill and "null" in lowered and "back-compat" in lowered)
            or ("composerIdentifier" in self.skill and "v0.6" in self.skill)
        )
        self.assertTrue(
            has_back_compat,
            "audit/SKILL.md must document v0.6 back-compat: no composers[] → composerIdentifier: null"
        )

    def test_skill_references_v07_for_iteration(self):
        """SKILL must mark this as a v0.7 capability."""
        self.assertIn(
            "v0.7",
            self.skill,
            "audit/SKILL.md must reference v0.7 for per-composer iteration"
        )

    def test_skill_documents_multi_call_site_path_handling(self):
        """For multi-call-site composers (path is array), composerIdentifier should reference first path."""
        # Either the SKILL documents the first-path rule, or it says "the composer's path".
        lowered = self.skill.lower()
        has_path_rule = (
            ("first path" in lowered)
            or ("composer's path" in lowered)
            or ("composer path" in lowered)
        )
        self.assertTrue(
            has_path_rule,
            "audit/SKILL.md must document how composerIdentifier maps to composer path "
            "(including multi-call-site groups where path is an array)"
        )


if __name__ == "__main__":
    unittest.main()
