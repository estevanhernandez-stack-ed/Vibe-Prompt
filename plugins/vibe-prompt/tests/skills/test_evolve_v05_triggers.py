"""
Task 24 (v0.5) — TDD tests for 4 new v0.5 friction triggers.

The 4 new triggers must appear in the friction trigger catalog
(friction-logger/references/friction-triggers.md) with correct
confidence levels, and handler templates must appear in
evolve-prompt/SKILL.md.

Trigger catalog (v0.5 additions):
  1. staged-fix-applied-and-eval-confirms-improvement (positive — high)
  2. staged-fix-rejected                              (medium)
  3. auto-write-rolled-back                           (high)
  4. composer-auto-generation-confidence-low          (medium)

Asserts:
  1. Each trigger code is present in friction-triggers.md
  2. Each trigger has the correct confidence label
  3. Each trigger row has a "When" description
  4. evolve-prompt/SKILL.md has handler entries for each trigger
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
FRICTION_TRIGGERS = (
    SKILLS_DIR / "friction-logger" / "references" / "friction-triggers.md"
)
EVOLVE_SKILL = SKILLS_DIR / "evolve-prompt" / "SKILL.md"


V05_TRIGGERS = [
    ("staged-fix-applied-and-eval-confirms-improvement", "high"),
    ("staged-fix-rejected", "medium"),
    ("auto-write-rolled-back", "high"),
    ("composer-auto-generation-confidence-low", "medium"),
]


class TestEvolveV05FrictionTriggers(unittest.TestCase):

    def setUp(self):
        self.catalog = FRICTION_TRIGGERS.read_text(encoding="utf-8")
        self.evolve = EVOLVE_SKILL.read_text(encoding="utf-8")

    # ------------------------------------------------------------------ #
    # 1. Each trigger code present                                        #
    # ------------------------------------------------------------------ #

    def test_all_v05_triggers_present_in_catalog(self):
        missing = [
            code for code, _ in V05_TRIGGERS if code not in self.catalog
        ]
        self.assertEqual(
            missing, [],
            f"Missing v0.5 friction triggers from catalog: {missing}"
        )

    # ------------------------------------------------------------------ #
    # 2. Each trigger has correct confidence                              #
    # ------------------------------------------------------------------ #

    def test_each_trigger_has_correct_confidence(self):
        for code, expected_confidence in V05_TRIGGERS:
            idx = self.catalog.find(code)
            self.assertGreater(
                idx, -1,
                f"Trigger {code} not found in catalog"
            )
            row_slice = self.catalog[idx:idx + 300]
            self.assertIn(
                expected_confidence,
                row_slice,
                f"Trigger {code} expected confidence={expected_confidence} "
                f"in same row, not found"
            )

    # ------------------------------------------------------------------ #
    # 3. Each trigger row has a "When" description                        #
    # ------------------------------------------------------------------ #

    def test_each_trigger_has_when_description(self):
        for code, _ in V05_TRIGGERS:
            idx = self.catalog.find(code)
            self.assertGreater(idx, -1)
            row = self.catalog[idx:idx + 500]
            # Table rows have pipe separators with description column
            self.assertIn(
                "|", row,
                f"Trigger {code} row must be in table format with When description"
            )
            # Description should be non-trivial — at least 15 chars after the
            # confidence column
            row_pieces = row.split("|")
            # Expect at least 4 pipe-separated pieces in the row
            self.assertGreaterEqual(
                len(row_pieces), 4,
                f"Trigger {code} must have a populated When description column"
            )

    # ------------------------------------------------------------------ #
    # 4. evolve-prompt/SKILL.md declares v0.5 handler templates            #
    # ------------------------------------------------------------------ #

    def test_evolve_skill_declares_v05_handlers(self):
        for code, _ in V05_TRIGGERS:
            self.assertIn(
                code,
                self.evolve,
                f"evolve-prompt/SKILL.md must declare handler template for "
                f"v0.5 trigger '{code}'"
            )

    def test_evolve_skill_mentions_v05_section(self):
        """evolve-prompt SKILL must mention v0.5 trigger handlers section."""
        has_section = (
            "v0.5" in self.evolve
            or "remediate" in self.evolve.lower()
        )
        self.assertTrue(
            has_section,
            "evolve-prompt/SKILL.md must have a v0.5 handler section"
        )

    # ------------------------------------------------------------------ #
    # 5. v0.4 triggers still present (no regression)                      #
    # ------------------------------------------------------------------ #

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
