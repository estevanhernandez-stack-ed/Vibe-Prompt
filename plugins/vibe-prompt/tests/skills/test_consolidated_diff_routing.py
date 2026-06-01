"""
Task 29 — TDD tests for F10+F11(+F12-high) consolidated-diff routing
declared in remediate/SKILL.md.

Asserts:
- remediate/SKILL.md describes consolidation step
- F10+F11 on same call site → ONE consolidated Category C diff
- F10+F11+F12-high → ONE consolidated diff; F12-high tracked + commented
- F10 + F11 on different sites → NO consolidation
- F10+F11+F12-critical → consolidation does NOT apply (auto-handoff path)
- Top-level consolidatedDiffs[] array populated in remediate-result.json
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
REMEDIATE_SKILL = SKILLS_DIR / "remediate" / "SKILL.md"


class TestConsolidatedDiffRouting(unittest.TestCase):

    def setUp(self):
        self.skill = REMEDIATE_SKILL.read_text(encoding="utf-8")
        self.lower = self.skill.lower()

    def test_skill_describes_consolidation_step(self):
        self.assertTrue(
            "consolidat" in self.lower,
            "remediate SKILL.md must describe consolidation step",
        )

    def test_skill_references_consolidation_rules_md(self):
        self.assertIn(
            "consolidation-rules.md",
            self.skill,
            "remediate SKILL.md must reference consolidation-rules.md",
        )

    def test_skill_describes_f10_f11_consolidation(self):
        self.assertIn(
            "F10",
            self.skill,
            "remediate SKILL.md must reference F10 for consolidation",
        )
        self.assertIn(
            "F11",
            self.skill,
            "remediate SKILL.md must reference F11 for consolidation",
        )

    def test_skill_describes_same_call_site_trigger(self):
        # Consolidation fires when findings are on the same call site
        self.assertTrue(
            "same call site" in self.lower or "same prompt" in self.lower or "same promptLocation" in self.lower or "same promptlocation" in self.lower,
            "remediate SKILL.md must declare same-call-site as the consolidation trigger",
        )

    def test_skill_describes_one_consolidated_diff(self):
        # When triggered, one consolidated Category C diff emerges
        # Use the consolidation section
        self.assertTrue(
            "one consolidated" in self.lower or "single consolidated" in self.lower or "consolidated category c" in self.lower or "consolidated diff" in self.lower,
            "remediate SKILL.md must describe emitting ONE consolidated diff",
        )

    def test_skill_describes_f12_high_inclusion(self):
        # F12-high folds into the consolidation
        idx = self.skill.find("F12-high")
        self.assertGreater(idx, -1, "remediate SKILL.md must reference F12-high explicitly")

    def test_skill_describes_f12_critical_exclusion(self):
        # F12-critical does NOT consolidate (uses auto-handoff path)
        self.assertIn(
            "F12-critical",
            self.skill,
            "remediate SKILL.md must reference F12-critical exclusion from consolidation",
        )

    def test_skill_describes_consolidated_diffs_array(self):
        # remediate-result.json gets a top-level consolidatedDiffs[] array
        self.assertIn(
            "consolidatedDiffs",
            self.skill,
            "remediate SKILL.md must populate top-level consolidatedDiffs[] in result",
        )

    def test_skill_describes_consolidated_finding_ids(self):
        # pending-fix front-matter carries consolidatedFindingIds
        self.assertIn(
            "consolidatedFindingIds",
            self.skill,
            "remediate SKILL.md must describe consolidatedFindingIds in pending front-matter",
        )

    def test_skill_describes_different_call_sites_no_consolidation(self):
        # F10 on call site A + F11 on call site B → NO consolidation
        idx_when = self.skill.lower().find("different call site")
        idx_alt = self.skill.lower().find("when not to consolidate")
        self.assertTrue(
            idx_when > -1 or idx_alt > -1,
            "remediate SKILL.md must address different-call-site exclusion",
        )

    def test_skill_describes_consolidation_step_order(self):
        # Consolidation must happen BEFORE confidence routing (so the single
        # diff carries the cluster's weighted confidence)
        # Acceptable wording: "consolidate before route" or "consolidate ... route"
        self.assertTrue(
            "before route" in self.lower or "before routing" in self.lower or "prior to routing" in self.lower or "consolidation step" in self.lower,
            "remediate SKILL.md must describe consolidation step ordering relative to routing",
        )


if __name__ == "__main__":
    unittest.main()
