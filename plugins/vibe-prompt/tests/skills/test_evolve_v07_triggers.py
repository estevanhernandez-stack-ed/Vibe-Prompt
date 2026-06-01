"""
Task 34 (v0.7) — TDD tests for 9 new v0.7 friction triggers.

The 9 new triggers must appear in the friction trigger catalog
(friction-logger/references/friction-triggers.md) with correct
confidence levels, and handler templates must appear in
evolve-prompt/SKILL.md.

Trigger catalog (v0.7 additions):
  1. composer-multiplicity-detected                                  (positive)
  2. composer-kind-detection-ambiguous                                (medium)
  3. workspace-detection-confidence-low                               (medium)
  4. scan-excludes-recommended-but-not-applied                        (low)
  5. category-d-migration-applied-and-eval-confirms-no-regression     (positive)
  6. category-d-migration-rejected                                    (low)
  7. f6-suspect-model-detected                                        (medium)
  8. consolidated-diff-closes-multiple-findings                       (positive)
  9. f12-severity-no-longer-degraded-by-composer-multiplicity         (positive)

Asserts:
  1. Each trigger code is present in friction-triggers.md
  2. Each trigger has the correct confidence label in the catalog row
  3. Each trigger row has a "When" description (pipe-table format)
  4. evolve-prompt/SKILL.md declares handler entries for each trigger
  5. evolve-prompt SKILL declares a v0.7 handler section
  6. v0.4 + v0.5 + v0.6 triggers still present (no regression)
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
FRICTION_TRIGGERS = (
    SKILLS_DIR / "friction-logger" / "references" / "friction-triggers.md"
)
EVOLVE_SKILL = SKILLS_DIR / "evolve-prompt" / "SKILL.md"


V07_TRIGGERS = [
    ("composer-multiplicity-detected", "positive"),
    ("composer-kind-detection-ambiguous", "medium"),
    ("workspace-detection-confidence-low", "medium"),
    ("scan-excludes-recommended-but-not-applied", "low"),
    ("category-d-migration-applied-and-eval-confirms-no-regression",
     "positive"),
    ("category-d-migration-rejected", "low"),
    ("f6-suspect-model-detected", "medium"),
    ("consolidated-diff-closes-multiple-findings", "positive"),
    ("f12-severity-no-longer-degraded-by-composer-multiplicity", "positive"),
]


class TestEvolveV07FrictionTriggers(unittest.TestCase):

    def setUp(self):
        self.catalog = FRICTION_TRIGGERS.read_text(encoding="utf-8")
        self.evolve = EVOLVE_SKILL.read_text(encoding="utf-8")

    # ------------------------------------------------------------------ #
    # 1. Each trigger code present                                        #
    # ------------------------------------------------------------------ #

    def test_all_v07_triggers_present_in_catalog(self):
        missing = [
            code for code, _ in V07_TRIGGERS if code not in self.catalog
        ]
        self.assertEqual(
            missing, [],
            f"Missing v0.7 friction triggers from catalog: {missing}"
        )

    # ------------------------------------------------------------------ #
    # 2. Each trigger has correct confidence in its catalog row           #
    # ------------------------------------------------------------------ #

    def test_each_trigger_has_correct_confidence(self):
        for code, expected_confidence in V07_TRIGGERS:
            idx = self.catalog.find(code)
            self.assertGreater(
                idx, -1,
                f"Trigger {code} not found in catalog"
            )
            row_slice = self.catalog[idx:idx + 500]
            self.assertIn(
                expected_confidence,
                row_slice,
                f"Trigger {code} expected confidence={expected_confidence} "
                f"in same row, not found"
            )

    # ------------------------------------------------------------------ #
    # 3. Each trigger row is in pipe-table format with description column #
    # ------------------------------------------------------------------ #

    def test_each_trigger_has_when_description(self):
        for code, _ in V07_TRIGGERS:
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
    # 4. evolve-prompt/SKILL.md declares v0.7 handler templates           #
    # ------------------------------------------------------------------ #

    def test_evolve_skill_declares_v07_handlers(self):
        for code, _ in V07_TRIGGERS:
            self.assertIn(
                code,
                self.evolve,
                f"evolve-prompt/SKILL.md must declare handler template for "
                f"v0.7 trigger '{code}'"
            )

    def test_evolve_skill_mentions_v07_section(self):
        """evolve-prompt SKILL must mention a v0.7 handler section."""
        self.assertIn(
            "v0.7",
            self.evolve,
            "evolve-prompt/SKILL.md must have a v0.7 handler section heading"
        )

    # ------------------------------------------------------------------ #
    # 5. Prior triggers still present (no regression)                     #
    # ------------------------------------------------------------------ #

    def test_v06_triggers_still_present(self):
        v06 = [
            "f12-api-parameter-detection-low-confidence",
            "auto-handoff-vibe-sec-completed",
            "auto-handoff-vibe-sec-unavailable",
            "f13-fired-but-prompt-intentionally-flexible-output",
            "f13-recommended-fix-applied-and-eval-confirms-output-stability",
            "category-b-voice-frame-detection-confidence-low",
            "category-b-voice-frame-rewrite-rejected",
        ]
        missing = [t for t in v06 if t not in self.catalog]
        self.assertEqual(
            missing, [],
            f"v0.6 triggers missing from catalog: {missing}"
        )

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
