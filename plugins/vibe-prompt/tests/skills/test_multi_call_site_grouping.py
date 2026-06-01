"""
Task 18 — TDD tests for multi-call-site grouping logic in first-run-setup (v0.7).

v0.7 multi-call-site kind groups inline SDK call sites into logical composer
clusters. Grouping heuristic: same-SDK + same-persona → one cluster; differing
personas → separate clusters; mixed SDKs → always separate.

WeSeeYou worked example: 6 inline call sites, 4 share "movie-trivia-bot"
persona + Gemini SDK → one composer entry; 2 share "badge-generator" persona +
Gemini SDK → second composer entry. Total composers[] length 2 under
kind: "multi-call-site". Each composer's path is an array of call-site paths.

Asserts:
  1. SKILL.md documents multi-call-site grouping step
  2. composer-kinds.md describes grouping heuristic (same SDK + same persona)
  3. composer-kinds.md states differing personas → separate clusters
  4. composer-kinds.md states mixed SDKs always separate
  5. WeSeeYou worked example: 6 sites → 2 composer entries (4+2 partition)
  6. SKILL.md / composer-kinds.md states path is string array for multi-call-site
  7. Confidence calibration documented for grouping clarity
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
FIRST_RUN_SKILL = SKILLS_DIR / "first-run-setup" / "SKILL.md"
COMPOSER_KINDS = SKILLS_DIR / "first-run-setup" / "references" / "composer-kinds.md"


class TestMultiCallSiteGrouping(unittest.TestCase):

    def setUp(self):
        self.skill = FIRST_RUN_SKILL.read_text(encoding="utf-8")
        self.kinds = COMPOSER_KINDS.read_text(encoding="utf-8")

    def test_skill_documents_grouping_step(self):
        """SKILL.md must document multi-call-site grouping step."""
        has_group_step = (
            "multi-call-site" in self.skill
            and ("group" in self.skill.lower() or "cluster" in self.skill.lower())
        )
        self.assertTrue(
            has_group_step,
            "first-run-setup/SKILL.md must document multi-call-site grouping step"
        )

    def test_grouping_heuristic_same_sdk_same_persona(self):
        """composer-kinds.md must declare same-SDK + same-persona grouping rule."""
        has_rule = (
            "Same SDK" in self.kinds
            or ("same-SDK" in self.kinds and "same persona" in self.kinds.lower())
            or ("same SDK" in self.kinds and "same persona" in self.kinds.lower())
        )
        # Lower-case variants
        kinds_lower = self.kinds.lower()
        rule_loose = (
            "same sdk" in kinds_lower
            and "same persona" in kinds_lower
            and "group" in kinds_lower
        )
        self.assertTrue(
            has_rule or rule_loose,
            "composer-kinds.md must declare same-SDK + same-persona grouping rule"
        )

    def test_differing_personas_separate_clusters(self):
        """composer-kinds.md must state differing personas → separate clusters."""
        kinds_lower = self.kinds.lower()
        has_separate = (
            ("differing" in kinds_lower or "different" in kinds_lower)
            and "persona" in kinds_lower
            and ("separate" in kinds_lower or "distinct" in kinds_lower)
        )
        self.assertTrue(
            has_separate,
            "composer-kinds.md must declare differing personas → separate groups"
        )

    def test_mixed_sdks_always_separate(self):
        """composer-kinds.md must state mixed SDKs always separate groups."""
        kinds_lower = self.kinds.lower()
        has_mixed = (
            "mixed sdk" in kinds_lower
            or "different sdk" in kinds_lower
            or ("Anthropic" in self.kinds and "Gemini" in self.kinds and "separate" in kinds_lower)
        )
        self.assertTrue(
            has_mixed,
            "composer-kinds.md must state mixed SDKs always separate groups"
        )

    def test_weseeyou_grouping_example(self):
        """composer-kinds.md must include WeSeeYou worked example: 6 sites → 2 entries (4+2)."""
        has_we = "WeSeeYou" in self.kinds
        has_count = ("6" in self.kinds or "six" in self.kinds.lower()) and (
            "4" in self.kinds or "4 call sites" in self.kinds.lower() or "movie-trivia" in self.kinds.lower()
        )
        self.assertTrue(
            has_we and has_count,
            "composer-kinds.md must include WeSeeYou worked example (6 inline → 2 grouped composers)"
        )

    def test_path_is_string_array_for_multi_call_site(self):
        """SKILL.md or composer-kinds.md must declare path is string[] for multi-call-site."""
        text = self.skill + self.kinds
        has_array = (
            ("string array" in text.lower() or "string[]" in text.lower() or "array of call-site" in text.lower())
            and "multi-call-site" in text
        )
        self.assertTrue(
            has_array,
            "first-run-setup/SKILL.md or composer-kinds.md must declare path is string array for multi-call-site"
        )

    def test_grouping_confidence_calibration(self):
        """composer-kinds.md must document confidence calibration for grouping clarity."""
        has_calibration = (
            "confidence" in self.kinds.lower()
            and ("calibration" in self.kinds.lower() or "0.85" in self.kinds or "0.70" in self.kinds or "0.7" in self.kinds)
        )
        self.assertTrue(
            has_calibration,
            "composer-kinds.md must document confidence calibration for grouping clarity"
        )


if __name__ == "__main__":
    unittest.main()
