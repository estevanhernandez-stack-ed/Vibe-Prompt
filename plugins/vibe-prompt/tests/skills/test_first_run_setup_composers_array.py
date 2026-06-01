"""
Task 16 — TDD tests for composers[] array emission in first-run-setup (v0.7).

v0.7 emits a composers[] array on composer.json. For single-composer apps,
composers[0] is a back-compat shim mirroring the top-level layers[] (both
fields written). For multi-composer / multi-call-site / shared-package,
top-level layers[] is omitted and composers[] is the source of truth.

Each composer entry has: kind, path, layers[], globalConfidence,
regenerationSource, apiParameterCompleteness.

Asserts:
  1. SKILL.md documents composers[] emission
  2. SKILL.md documents per-composer required fields (path, layers, globalConfidence, regenerationSource, apiParameterCompleteness)
  3. SKILL.md states top-level layers[] is omitted for multi-* kinds
  4. SKILL.md states top-level layers[] mirror for single-composer (back-compat)
  5. apiParameterCompleteness emission documented
  6. v0.6 composer.json (no composers[]) downstream-readable via top-level layers[] (back-compat preserved)
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
FIRST_RUN_SKILL = SKILLS_DIR / "first-run-setup" / "SKILL.md"


class TestFirstRunSetupComposersArray(unittest.TestCase):

    def setUp(self):
        self.skill = FIRST_RUN_SKILL.read_text(encoding="utf-8")

    def test_skill_documents_composers_array_emission(self):
        """SKILL.md must declare composers[] array emission."""
        has_composers = "composers[]" in self.skill or "composers[" in self.skill
        self.assertTrue(
            has_composers,
            "first-run-setup/SKILL.md must declare composers[] array emission"
        )

    def test_skill_documents_per_composer_required_fields(self):
        """Each composer entry must have kind, path, layers, globalConfidence, regenerationSource, apiParameterCompleteness."""
        for field in ["kind", "path", "layers", "globalConfidence", "regenerationSource", "apiParameterCompleteness"]:
            self.assertIn(
                field,
                self.skill,
                f"first-run-setup/SKILL.md must document per-composer field '{field}'"
            )

    def test_skill_omits_top_level_layers_for_multi(self):
        """For multi-composer / multi-call-site / shared-package, top-level layers[] is omitted."""
        # The SKILL must declare this distinction
        has_omit_clause = (
            "omit" in self.skill.lower()
            and ("multi-composer" in self.skill or "multi-call-site" in self.skill)
        )
        self.assertTrue(
            has_omit_clause,
            "first-run-setup/SKILL.md must declare top-level layers[] omitted for multi-* kinds"
        )

    def test_skill_writes_layers_shim_for_single_composer(self):
        """For single-composer, top-level layers[] is written as a back-compat shim mirroring composers[0]."""
        has_shim = (
            ("single-composer" in self.skill)
            and ("shim" in self.skill.lower() or "back-compat" in self.skill.lower() or "backward compat" in self.skill.lower())
        )
        self.assertTrue(
            has_shim,
            "first-run-setup/SKILL.md must declare top-level layers[] back-compat shim for single-composer"
        )

    def test_apiparameter_completeness_emission_documented(self):
        """apiParameterCompleteness per composer must be documented."""
        has_apc = "apiParameterCompleteness" in self.skill
        self.assertTrue(
            has_apc,
            "first-run-setup/SKILL.md must declare apiParameterCompleteness emission"
        )

    def test_apiparameter_completeness_fraction_semantic(self):
        """apiParameterCompleteness should be documented as fraction-of-layers-with-non-null-apiParameter."""
        has_semantic = (
            "fraction" in self.skill.lower()
            or "ratio" in self.skill.lower()
            or "non-null" in self.skill.lower()
        )
        self.assertTrue(
            has_semantic,
            "first-run-setup/SKILL.md must document apiParameterCompleteness as fraction-of-layers-with-non-null-apiParameter"
        )

    def test_v06_back_compat_via_top_level_layers(self):
        """v0.6 composer.json (without composers[]) is still readable via top-level layers[]."""
        # The SKILL should state v0.6-style consumers can fall back to top-level layers[]
        has_back_compat = (
            "back-compat" in self.skill.lower()
            or "backward compat" in self.skill.lower()
            or "v0.6" in self.skill
        )
        self.assertTrue(
            has_back_compat,
            "first-run-setup/SKILL.md must document back-compat reading via top-level layers[]"
        )

    def test_v07_emission_phase_documented(self):
        """SKILL.md must document the v0.7 emission phase explicitly (so multi-* kinds populate composers[])."""
        has_v07 = "v0.7" in self.skill
        self.assertTrue(
            has_v07,
            "first-run-setup/SKILL.md must document v0.7 composers[] emission phase"
        )


if __name__ == "__main__":
    unittest.main()
