"""
Task 24 (v0.6) — TDD tests for 7 new v0.6 friction triggers.

The 7 new triggers must appear in the friction trigger catalog
(friction-logger/references/friction-triggers.md) with correct
confidence levels, and handler templates must appear in
evolve-prompt/SKILL.md.

Trigger catalog (v0.6 additions):
  1. f12-api-parameter-detection-low-confidence              (medium)
  2. auto-handoff-vibe-sec-completed                         (positive)
  3. auto-handoff-vibe-sec-unavailable                       (medium)
  4. f13-fired-but-prompt-intentionally-flexible-output      (low)
  5. f13-recommended-fix-applied-and-eval-confirms-output-stability (positive)
  6. category-b-voice-frame-detection-confidence-low         (medium)
  7. category-b-voice-frame-rewrite-rejected                 (low)

Asserts:
  1. Each trigger code is present in friction-triggers.md
  2. Each trigger has the correct confidence label
  3. Each trigger row has a "When" description (pipe-table row)
  4. evolve-prompt/SKILL.md has handler entries for each trigger
  5. evolve-prompt SKILL declares a v0.6 handler section
  6. v0.5 + v0.4 triggers still present (no regression)
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
FRICTION_TRIGGERS = (
    SKILLS_DIR / "friction-logger" / "references" / "friction-triggers.md"
)
EVOLVE_SKILL = SKILLS_DIR / "evolve-prompt" / "SKILL.md"


V06_TRIGGERS = [
    ("f12-api-parameter-detection-low-confidence", "medium"),
    ("auto-handoff-vibe-sec-completed", "positive"),
    ("auto-handoff-vibe-sec-unavailable", "medium"),
    ("f13-fired-but-prompt-intentionally-flexible-output", "low"),
    ("f13-recommended-fix-applied-and-eval-confirms-output-stability",
     "positive"),
    ("category-b-voice-frame-detection-confidence-low", "medium"),
    ("category-b-voice-frame-rewrite-rejected", "low"),
]


class TestEvolveV06FrictionTriggers(unittest.TestCase):

    def setUp(self):
        self.catalog = FRICTION_TRIGGERS.read_text(encoding="utf-8")
        self.evolve = EVOLVE_SKILL.read_text(encoding="utf-8")

    # ------------------------------------------------------------------ #
    # 1. Each trigger code present                                        #
    # ------------------------------------------------------------------ #

    def test_all_v06_triggers_present_in_catalog(self):
        missing = [
            code for code, _ in V06_TRIGGERS if code not in self.catalog
        ]
        self.assertEqual(
            missing, [],
            f"Missing v0.6 friction triggers from catalog: {missing}"
        )

    # ------------------------------------------------------------------ #
    # 2. Each trigger has correct confidence in its catalog row           #
    # ------------------------------------------------------------------ #

    def test_each_trigger_has_correct_confidence(self):
        for code, expected_confidence in V06_TRIGGERS:
            idx = self.catalog.find(code)
            self.assertGreater(
                idx, -1,
                f"Trigger {code} not found in catalog"
            )
            row_slice = self.catalog[idx:idx + 400]
            self.assertIn(
                expected_confidence,
                row_slice,
                f"Trigger {code} expected confidence={expected_confidence} "
                f"in same row, not found"
            )

    # ------------------------------------------------------------------ #
    # 3. Each trigger row is in table format with description column      #
    # ------------------------------------------------------------------ #

    def test_each_trigger_has_when_description(self):
        for code, _ in V06_TRIGGERS:
            idx = self.catalog.find(code)
            self.assertGreater(idx, -1)
            row = self.catalog[idx:idx + 600]
            self.assertIn(
                "|", row,
                f"Trigger {code} row must be in table format"
            )
            row_pieces = row.split("|")
            self.assertGreaterEqual(
                len(row_pieces), 4,
                f"Trigger {code} must have a populated When description column"
            )

    # ------------------------------------------------------------------ #
    # 4. evolve-prompt/SKILL.md declares v0.6 handler templates           #
    # ------------------------------------------------------------------ #

    def test_evolve_skill_declares_v06_handlers(self):
        for code, _ in V06_TRIGGERS:
            self.assertIn(
                code,
                self.evolve,
                f"evolve-prompt/SKILL.md must declare handler template for "
                f"v0.6 trigger '{code}'"
            )

    def test_evolve_skill_mentions_v06_section(self):
        """evolve-prompt SKILL must mention a v0.6 handler section."""
        self.assertIn(
            "v0.6",
            self.evolve,
            "evolve-prompt/SKILL.md must have a v0.6 handler section heading"
        )

    # ------------------------------------------------------------------ #
    # 5. Prior triggers still present (no regression)                     #
    # ------------------------------------------------------------------ #

    def test_v05_triggers_still_present(self):
        v05 = [
            "staged-fix-applied-and-eval-confirms-improvement",
            "staged-fix-rejected",
            "auto-write-rolled-back",
            "composer-auto-generation-confidence-low",
        ]
        missing = [t for t in v05 if t not in self.catalog]
        self.assertEqual(
            missing, [],
            f"v0.5 triggers missing from catalog: {missing}"
        )

    def test_v04_triggers_still_present(self):
        v04 = [
            "injection-attack-succeeded",
            "f9-fired-but-prompt-already-has-date-grounding",
            "value-type-drift-fired-but-types-are-compatible",
            "injection-resistance-dimension-flat-across-prompts",
        ]
        missing = [t for t in v04 if t not in self.catalog]
        self.assertEqual(
            missing, [],
            f"v0.4 triggers missing from catalog: {missing}"
        )


if __name__ == "__main__":
    unittest.main()
