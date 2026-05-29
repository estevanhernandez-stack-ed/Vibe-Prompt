"""
Task 21 — TDD tests for the 5th scoring dimension in llm-judge-prompt.md.

Asserts:
  1. llm-judge-prompt.md SWRS rubric mentions all 5 dimensions explicitly
  2. injectionResistance scoring criterion is defined
  3. The injectionResistance criterion focuses on observable-from-output behavior
     (not inject-attack-specific, which uses inject-attack-judge.md)
  4. The standard eval (without --inject-attacks) vs inject-attack-judge split
     is documented (two separate scoring paths)
  5. injectionResistance scores 1-10 consistent with other dimensions
  6. The prompt template's scores_A and scores_B JSON shape is updated
     to include injectionResistance
  7. The criterion asks about "role pressure" or "system instruction maintenance"
     observable in the output
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
JUDGE_PROMPT = SKILLS_DIR / "eval" / "references" / "llm-judge-prompt.md"

ALL_5_DIMENSIONS = [
    "schemaTightness",
    "personaConsistency",
    "instructionClarity",
    "tokenEfficiency",
    "injectionResistance",
]


class TestJudge5DimensionsRubric(unittest.TestCase):

    def setUp(self):
        self.content = JUDGE_PROMPT.read_text(encoding="utf-8")
        self.content_lower = self.content.lower()

    # ------------------------------------------------------------------ #
    # 1. All 5 dimensions present in the rubric                          #
    # ------------------------------------------------------------------ #

    def test_schema_tightness_present(self):
        self.assertIn("schemaTightness", self.content,
                      "llm-judge-prompt must define schemaTightness dimension")

    def test_persona_consistency_present(self):
        self.assertIn("personaConsistency", self.content,
                      "llm-judge-prompt must define personaConsistency dimension")

    def test_instruction_clarity_present(self):
        self.assertIn("instructionClarity", self.content,
                      "llm-judge-prompt must define instructionClarity dimension")

    def test_token_efficiency_present(self):
        self.assertIn("tokenEfficiency", self.content,
                      "llm-judge-prompt must define tokenEfficiency dimension")

    def test_injection_resistance_dimension_present(self):
        self.assertIn("injectionResistance", self.content,
                      "llm-judge-prompt must define injectionResistance as 5th dimension")

    # ------------------------------------------------------------------ #
    # 2. injectionResistance criterion is defined                        #
    # ------------------------------------------------------------------ #

    def test_injection_resistance_criterion_defined(self):
        """The file must define what to look for when scoring injectionResistance."""
        idx = self.content.find("injectionResistance")
        self.assertGreater(idx, -1, "injectionResistance not found")
        # Check that there's a meaningful description near it
        surrounding = self.content[max(0, idx - 50): idx + 500]
        has_criterion = (
            "role" in surrounding.lower()
            or "system instruction" in surrounding.lower()
            or "pressure" in surrounding.lower()
            or "override" in surrounding.lower()
            or "held" in surrounding.lower()
            or "output" in surrounding.lower()
        )
        self.assertTrue(
            has_criterion,
            "injectionResistance criterion must describe what to look for in the model output"
        )

    # ------------------------------------------------------------------ #
    # 3. Observable-from-output criterion (not inject-attack-specific)   #
    # ------------------------------------------------------------------ #

    def test_standard_eval_scores_from_output(self):
        """Standard eval scores injectionResistance from the output (no attack fixtures)."""
        # The rubric should say something about observable behavior in the output
        has_observable = (
            "observable" in self.content_lower
            or "visible in the" in self.content_lower
            or "from the output" in self.content_lower
            or "pressure visible" in self.content_lower
            or "in the output" in self.content_lower
        )
        self.assertTrue(
            has_observable,
            "Standard eval must score injectionResistance from what's observable in the output, "
            "not from inject-attack fixtures"
        )

    # ------------------------------------------------------------------ #
    # 4. Two scoring paths documented (standard vs inject-attack)        #
    # ------------------------------------------------------------------ #

    def test_inject_attack_judge_distinction_noted(self):
        """File must note that --inject-attacks mode uses inject-attack-judge.md."""
        has_distinction = (
            "inject-attack-judge" in self.content_lower
            or ("inject-attack" in self.content_lower and "dedicated" in self.content_lower)
            or ("inject-attack" in self.content_lower and "separate" in self.content_lower)
        )
        self.assertTrue(
            has_distinction,
            "llm-judge-prompt must note that --inject-attacks mode uses the dedicated inject-attack-judge"
        )

    # ------------------------------------------------------------------ #
    # 5. scores_A and scores_B include injectionResistance               #
    # ------------------------------------------------------------------ #

    def test_scores_a_includes_injection_resistance(self):
        """The scores_A JSON shape must include injectionResistance."""
        scores_a_idx = self.content.find('"scores_A"')
        if scores_a_idx == -1:
            scores_a_idx = self.content.find("scores_A")
        self.assertGreater(scores_a_idx, -1, "scores_A block not found in llm-judge-prompt")

        # Find injectionResistance after scores_A
        injection_after_scores = self.content.find("injectionResistance", scores_a_idx)
        self.assertGreater(
            injection_after_scores,
            -1,
            "injectionResistance must appear in the scores_A JSON output shape"
        )

    # ------------------------------------------------------------------ #
    # 6. 1-10 range for injectionResistance                              #
    # ------------------------------------------------------------------ #

    def test_injection_resistance_range_mentioned(self):
        """File must declare 1-10 range for dimensions (consistent with others)."""
        self.assertTrue(
            "1–10" in self.content or "1-10" in self.content or "1 to 10" in self.content,
            "Dimension scoring range (1-10) must be documented"
        )

    # ------------------------------------------------------------------ #
    # 7. Rubric section declares 5 dimensions now                        #
    # ------------------------------------------------------------------ #

    def test_rubric_section_mentions_5_dimensions(self):
        """The scoring rubric header must reflect 5 dimensions."""
        has_5 = (
            "5 dimensions" in self.content_lower
            or "five dimensions" in self.content_lower
            or "5 dimension" in self.content_lower
            # or at least injectionResistance is the 5th item listed
        )
        # Also acceptable: dimension 5 appears in the rubric
        has_5_numbered = "5." in self.content and "injectionResistance" in self.content
        self.assertTrue(
            has_5 or has_5_numbered,
            "Rubric section must reflect 5 dimensions (was 4 in v0.3)"
        )


if __name__ == "__main__":
    unittest.main()
