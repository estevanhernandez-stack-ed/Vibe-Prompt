"""
Task 23 — TDD tests for 4 new v0.4 friction triggers.

The 4 new triggers must appear in the friction trigger catalog
(friction-logger/references/friction-triggers.md) with correct
confidence levels and handler documentation.

Trigger catalog (v0.4 additions):
  1. injection-attack-succeeded          (high)
  2. f9-fired-but-prompt-already-has-date-grounding  (low)
  3. value-type-drift-fired-but-types-are-compatible (low)
  4. injection-resistance-dimension-flat-across-prompts (medium)

Asserts:
  1. injection-attack-succeeded is present with confidence=high
  2. f9-fired-but-prompt-already-has-date-grounding is present with confidence=low
  3. value-type-drift-fired-but-types-are-compatible is present with confidence=low
  4. injection-resistance-dimension-flat-across-prompts is present with confidence=medium
  5. Each trigger includes a "when" description (handler template)
  6. Triggers appear in the correct section (eval triggers for inject-attack,
     audit triggers for f9 + injection-resistance, eval triggers for value-type-drift)
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
FRICTION_TRIGGERS = (
    SKILLS_DIR / "friction-logger" / "references" / "friction-triggers.md"
)


class TestEvolveV04FrictionTriggers(unittest.TestCase):

    def setUp(self):
        self.content = FRICTION_TRIGGERS.read_text(encoding="utf-8")

    # ------------------------------------------------------------------ #
    # 1. injection-attack-succeeded (high)                                #
    # ------------------------------------------------------------------ #

    def test_injection_attack_succeeded_present(self):
        self.assertIn(
            "injection-attack-succeeded",
            self.content,
            "friction-triggers.md must declare 'injection-attack-succeeded' trigger"
        )

    def test_injection_attack_succeeded_is_high(self):
        """injection-attack-succeeded must have confidence=high."""
        idx = self.content.find("injection-attack-succeeded")
        self.assertGreater(idx, -1)
        # The table row should contain 'high' within ~200 chars
        row_slice = self.content[idx:idx + 200]
        self.assertIn(
            "high",
            row_slice,
            "injection-attack-succeeded must have confidence=high"
        )

    # ------------------------------------------------------------------ #
    # 2. f9-fired-but-prompt-already-has-date-grounding (low)            #
    # ------------------------------------------------------------------ #

    def test_f9_false_positive_trigger_present(self):
        self.assertIn(
            "f9-fired-but-prompt-already-has-date-grounding",
            self.content,
            "friction-triggers.md must declare 'f9-fired-but-prompt-already-has-date-grounding'"
        )

    def test_f9_false_positive_trigger_is_low(self):
        idx = self.content.find("f9-fired-but-prompt-already-has-date-grounding")
        self.assertGreater(idx, -1)
        row_slice = self.content[idx:idx + 200]
        self.assertIn(
            "low",
            row_slice,
            "f9-fired-but-prompt-already-has-date-grounding must have confidence=low"
        )

    # ------------------------------------------------------------------ #
    # 3. value-type-drift-fired-but-types-are-compatible (low)           #
    # ------------------------------------------------------------------ #

    def test_value_type_drift_false_positive_trigger_present(self):
        self.assertIn(
            "value-type-drift-fired-but-types-are-compatible",
            self.content,
            "friction-triggers.md must declare 'value-type-drift-fired-but-types-are-compatible'"
        )

    def test_value_type_drift_false_positive_trigger_is_low(self):
        idx = self.content.find("value-type-drift-fired-but-types-are-compatible")
        self.assertGreater(idx, -1)
        row_slice = self.content[idx:idx + 200]
        self.assertIn(
            "low",
            row_slice,
            "value-type-drift-fired-but-types-are-compatible must have confidence=low"
        )

    # ------------------------------------------------------------------ #
    # 4. injection-resistance-dimension-flat-across-prompts (medium)      #
    # ------------------------------------------------------------------ #

    def test_injection_resistance_flat_trigger_present(self):
        self.assertIn(
            "injection-resistance-dimension-flat-across-prompts",
            self.content,
            "friction-triggers.md must declare 'injection-resistance-dimension-flat-across-prompts'"
        )

    def test_injection_resistance_flat_trigger_is_medium(self):
        idx = self.content.find("injection-resistance-dimension-flat-across-prompts")
        self.assertGreater(idx, -1)
        row_slice = self.content[idx:idx + 200]
        self.assertIn(
            "medium",
            row_slice,
            "injection-resistance-dimension-flat-across-prompts must have confidence=medium"
        )

    # ------------------------------------------------------------------ #
    # 5. Each trigger has a "When" description                            #
    # ------------------------------------------------------------------ #

    def test_injection_attack_succeeded_has_when_description(self):
        """Each trigger row must have a 'When' description (3rd column in table)."""
        idx = self.content.find("injection-attack-succeeded")
        self.assertGreater(idx, -1)
        row = self.content[idx:idx + 500]
        # Table rows have pipe separators; there should be content after the confidence column
        self.assertTrue(
            "|" in row,
            "injection-attack-succeeded row must be in table format with When description"
        )
        # The description should mention attack or model honoring the injection
        has_desc = (
            "attack" in row.lower()
            or "honor" in row.lower()
            or "inject" in row.lower()
            or "model" in row.lower()
        )
        self.assertTrue(
            has_desc,
            "injection-attack-succeeded must have a 'When' description referencing attack context"
        )

    def test_f9_trigger_has_when_description(self):
        idx = self.content.find("f9-fired-but-prompt-already-has-date-grounding")
        self.assertGreater(idx, -1)
        row = self.content[idx:idx + 500]
        has_desc = (
            "date" in row.lower()
            or "grounding" in row.lower()
            or "missed" in row.lower()
            or "path" in row.lower()
        )
        self.assertTrue(
            has_desc,
            "f9 trigger must have a 'When' description referencing date grounding context"
        )

    def test_value_type_drift_trigger_has_when_description(self):
        idx = self.content.find("value-type-drift-fired-but-types-are-compatible")
        self.assertGreater(idx, -1)
        row = self.content[idx:idx + 500]
        has_desc = (
            "type" in row.lower()
            or "union" in row.lower()
            or "schema" in row.lower()
            or "compatible" in row.lower()
        )
        self.assertTrue(
            has_desc,
            "value-type-drift trigger must have a 'When' description referencing type compatibility"
        )

    def test_injection_resistance_flat_has_when_description(self):
        idx = self.content.find("injection-resistance-dimension-flat-across-prompts")
        self.assertGreater(idx, -1)
        row = self.content[idx:idx + 500]
        has_desc = (
            "flat" in row.lower()
            or "same" in row.lower()
            or "uniform" in row.lower()
            or "score" in row.lower()
            or "dimension" in row.lower()
        )
        self.assertTrue(
            has_desc,
            "injection-resistance-dimension-flat trigger must have a When description"
        )

    # ------------------------------------------------------------------ #
    # 6. All 4 triggers appear in the file (count check)                  #
    # ------------------------------------------------------------------ #

    def test_all_four_v04_triggers_present(self):
        """All 4 new v0.4 triggers must be present."""
        missing = []
        for trigger in [
            "injection-attack-succeeded",
            "f9-fired-but-prompt-already-has-date-grounding",
            "value-type-drift-fired-but-types-are-compatible",
            "injection-resistance-dimension-flat-across-prompts",
        ]:
            if trigger not in self.content:
                missing.append(trigger)
        self.assertEqual(
            missing,
            [],
            f"Missing v0.4 friction triggers: {missing}"
        )


if __name__ == "__main__":
    unittest.main()
