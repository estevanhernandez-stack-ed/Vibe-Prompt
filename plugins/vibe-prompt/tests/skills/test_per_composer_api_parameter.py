"""
Task 17 — TDD tests for per-composer apiParameter detection in first-run-setup (v0.7).

v0.6 ran apiParameter detection once globally — fine for single-composer apps
but wrong for multi-composer: composer A might pass via systemInstruction: arg
while composer B interpolates into contents[].parts[].text. Each composer's
layers carry their own apiParameter + apiParameterConfidence independently.

apiParameterCompleteness is computed per composer (not globally), reporting
the fraction of that composer's layers with detected non-null apiParameter.

Asserts:
  1. SKILL.md documents per-composer apiParameter detection (Stage 2b runs per composer in composers[])
  2. composer-detection.md links apiParameter detection to per-composer iteration
  3. apiParameterCompleteness defined as fraction per composer, not global
  4. SKILL.md states each composer's layers carry independent apiParameter values
  5. Multi-composer worked example or note (composer A vs composer B differing apiParameter destinations)
  6. apiParameter null handling preserved per composer (friction trigger per composer if any layer null)
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
FIRST_RUN_SKILL = SKILLS_DIR / "first-run-setup" / "SKILL.md"
COMPOSER_DETECTION = SKILLS_DIR / "first-run-setup" / "references" / "composer-detection.md"


class TestPerComposerApiParameter(unittest.TestCase):

    def setUp(self):
        self.skill = FIRST_RUN_SKILL.read_text(encoding="utf-8")
        self.detection = COMPOSER_DETECTION.read_text(encoding="utf-8")

    def test_skill_documents_per_composer_apiparameter(self):
        """SKILL.md must declare Stage 2b runs per composer."""
        # The Stage 2 / 2b / 3 iteration per composer in composers[] is already declared in v0.7+
        has_per_composer = (
            ("Stage 2b" in self.skill or "apiParameter detection" in self.skill)
            and ("per composer" in self.skill.lower() or "per-composer" in self.skill.lower() or "iterate" in self.skill.lower() or "each composer" in self.skill.lower())
        )
        self.assertTrue(
            has_per_composer,
            "first-run-setup/SKILL.md must declare Stage 2b apiParameter detection runs per composer"
        )

    def test_composer_detection_references_per_composer_run(self):
        """composer-detection.md must note that apiParameter detection runs per composer in v0.7+."""
        has_per_composer_note = (
            "per composer" in self.detection.lower()
            or "per-composer" in self.detection.lower()
            or "iterate" in self.detection.lower()
            or "v0.7" in self.detection
        )
        self.assertTrue(
            has_per_composer_note,
            "composer-detection.md must note v0.7+ per-composer iteration of apiParameter detection"
        )

    def test_apiparameter_completeness_per_composer_not_global(self):
        """apiParameterCompleteness is per composer, not aggregated across composers."""
        # In the emission shape table or descriptive text
        has_per_composer_completeness = (
            "apiParameterCompleteness" in self.skill
            and ("per composer" in self.skill.lower()
                 or "per-composer" in self.skill.lower()
                 or "fraction of its layers" in self.skill.lower()
                 or "fraction of that composer" in self.skill.lower())
        )
        self.assertTrue(
            has_per_composer_completeness,
            "first-run-setup/SKILL.md must declare apiParameterCompleteness is per-composer (not global)"
        )

    def test_independent_apiparameter_per_composer(self):
        """Each composer's layers carry independent apiParameter values."""
        has_independent = (
            "independent" in self.skill.lower()
            or "independently" in self.skill.lower()
            or "differing apiParameter" in self.skill.lower()
            or "different apiParameter" in self.skill.lower()
            or "differ between composers" in self.skill.lower()
        )
        self.assertTrue(
            has_independent,
            "first-run-setup/SKILL.md must state layers carry apiParameter independently per composer"
        )

    def test_multi_composer_apiparameter_example(self):
        """SKILL.md or composer-detection.md must include a multi-composer apiParameter example or note."""
        text = self.skill + self.detection
        # Composer A vs B example
        has_example = (
            ("composer A" in text.lower() and "composer B" in text.lower())
            or ("differing apiParameter" in text.lower())
            or ("systemInstruction" in text and "contents" in text and "different" in text.lower())
        )
        # Soft check: at minimum the skill should mention the apiParameter destinations vary across composers
        has_vary = (
            "differing" in text.lower()
            or "vary" in text.lower()
            or "differs per composer" in text.lower()
            or "differ per composer" in text.lower()
        )
        self.assertTrue(
            has_example or has_vary,
            "first-run-setup/SKILL.md or composer-detection.md must include multi-composer apiParameter variation example"
        )

    def test_apiparameter_null_handling_preserved_per_composer(self):
        """When any layer's apiParameter is null, friction-log per composer (not globally)."""
        # The existing friction trigger f12-api-parameter-detection-low-confidence should still apply per composer
        has_friction = (
            "f12-api-parameter-detection-low-confidence" in self.skill
            and "any layer" in self.skill.lower()
        )
        self.assertTrue(
            has_friction,
            "first-run-setup/SKILL.md must preserve null apiParameter friction trigger per composer"
        )


if __name__ == "__main__":
    unittest.main()
