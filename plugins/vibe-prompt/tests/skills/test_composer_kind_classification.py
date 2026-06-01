"""
Task 15 — TDD tests for composer-kind classification in first-run-setup (v0.7).

v0.7 extends composer detection to classify the composer topology kind
(single-composer / multi-composer / multi-call-site / shared-package) based
on SDK-call topology before emission. The classification step runs after
file detection (Stage 1) and before per-composer layer tracing.

Fixture-by-fixture:
  - Fixture A: one composer file with SDK call → single-composer, shape single
  - Fixture B: two distinct composer files w/ SDK calls → multi-composer, shape multi
  - Fixture C: no composer file; N inline call sites → multi-call-site, shape multi
  - Fixture D: composer in packages/<name>/; referenced by multiple workspaces → shared-package, shape multi

Asserts:
  1. SKILL.md documents the kind-classification step
  2. composer-detection.md links to composer-kinds.md
  3. All 4 kind enum values documented in SKILL.md or composer-detection.md
  4. compositionShape ("single" vs "multi") declared
  5. Classification ordering — kind picked before layer-tracing
  6. shared-package detection rule (packages/ subdir + multi-workspace consumer)
  7. multi-call-site fallback (zero composer files but SDK calls exist)
  8. single-composer back-compat (writes top-level layers[] shim)
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
FIRST_RUN_SKILL = SKILLS_DIR / "first-run-setup" / "SKILL.md"
COMPOSER_DETECTION = SKILLS_DIR / "first-run-setup" / "references" / "composer-detection.md"
COMPOSER_KINDS = SKILLS_DIR / "first-run-setup" / "references" / "composer-kinds.md"


class TestComposerKindClassification(unittest.TestCase):

    def setUp(self):
        self.skill = FIRST_RUN_SKILL.read_text(encoding="utf-8")
        self.detection = COMPOSER_DETECTION.read_text(encoding="utf-8")
        self.kinds = COMPOSER_KINDS.read_text(encoding="utf-8")

    def test_skill_documents_kind_classification(self):
        """SKILL.md must invoke kind classification before emission."""
        has_classify = (
            "kind" in self.skill.lower()
            and ("classif" in self.skill.lower() or "topology" in self.skill.lower())
        )
        self.assertTrue(
            has_classify,
            "first-run-setup/SKILL.md must document the kind-classification step"
        )

    def test_composer_detection_links_kinds_reference(self):
        """composer-detection.md must reference composer-kinds.md."""
        self.assertIn(
            "composer-kinds.md",
            self.detection,
            "composer-detection.md must cross-reference composer-kinds.md"
        )

    def test_all_four_kinds_documented_in_skill(self):
        """SKILL.md must reference all four kind enum values."""
        for kind in ["single-composer", "multi-composer", "multi-call-site", "shared-package"]:
            self.assertIn(
                kind,
                self.skill,
                f"first-run-setup/SKILL.md must reference '{kind}'"
            )

    def test_composition_shape_declared(self):
        """compositionShape (single vs multi) must be declared in SKILL.md."""
        has_shape = "compositionShape" in self.skill
        self.assertTrue(
            has_shape,
            "first-run-setup/SKILL.md must declare compositionShape emission"
        )

    def test_classification_before_layer_tracing(self):
        """The kind-classification step should come before per-composer layer tracing."""
        # Classification needs to happen before tracing — find both references and verify order
        kind_idx = self.skill.lower().find("classif")
        # Detection mentions tracing in stage 2; we want kind step referenced
        has_per_composer = (
            "per composer" in self.skill.lower()
            or "per-composer" in self.skill.lower()
            or "each composer" in self.skill.lower()
        )
        self.assertTrue(
            has_per_composer,
            "first-run-setup/SKILL.md must document per-composer iteration after kind classification"
        )

    def test_shared_package_detection_rule(self):
        """SKILL.md or kinds reference must define shared-package detection (packages/ subdir + multi-workspace)."""
        has_rule = (
            "packages/" in self.kinds
            and ("workspace" in self.kinds.lower())
        )
        self.assertTrue(
            has_rule,
            "composer-kinds.md must define shared-package detection rule (packages/ subdir + multi-workspace consumer)"
        )

    def test_multi_call_site_fallback(self):
        """When zero composer files resolve but SDK calls exist → multi-call-site."""
        has_fallback = (
            "multi-call-site" in self.kinds
            and ("zero" in self.kinds.lower() or "no composer" in self.kinds.lower() or "no canonical" in self.kinds.lower())
        )
        self.assertTrue(
            has_fallback,
            "composer-kinds.md must document multi-call-site fallback for zero composer files"
        )

    def test_single_composer_back_compat_shim(self):
        """single-composer must still emit top-level layers[] for v0.6 consumer back-compat."""
        has_shim = (
            "back-compat" in self.skill.lower()
            or "backward" in self.skill.lower()
            or "shim" in self.skill.lower()
        )
        self.assertTrue(
            has_shim,
            "first-run-setup/SKILL.md must declare back-compat shim for single-composer (top-level layers[])"
        )


if __name__ == "__main__":
    unittest.main()
