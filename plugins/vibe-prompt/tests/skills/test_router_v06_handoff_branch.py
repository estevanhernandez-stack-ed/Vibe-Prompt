"""
Task 23 (v0.6) — TDD tests for the review-vibe-sec-handoff-results state branch in router/SKILL.md.

New branch: "review-vibe-sec-handoff-results"
Trigger: .vibe-prompt/remediate/state/handoff-vibe-sec-*.json files exist.

Asserts:
  1. router/SKILL.md declares a new state branch for vibe-sec handoff results
  2. Branch is triggered when .vibe-prompt/remediate/state/handoff-vibe-sec-*.json exists
  3. Branch surfaces the vibe-sec finding list from the handoff result file
  4. Branch label references "review-vibe-sec-handoff-results"
  5. Branch fits into the existing numbered state-checks flow (doesn't break prior branches)
  6. v0.5 + v0.4 branches still present
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
ROUTER_SKILL = SKILLS_DIR / "router" / "SKILL.md"


class TestRouterV06HandoffVibeSecBranch(unittest.TestCase):

    def setUp(self):
        self.content = ROUTER_SKILL.read_text(encoding="utf-8")
        self.content_lower = self.content.lower()

    # ------------------------------------------------------------------ #
    # 1. handoff-vibe-sec branch declared                                 #
    # ------------------------------------------------------------------ #

    def test_handoff_vibe_sec_branch_declared(self):
        has_branch = (
            "review-vibe-sec-handoff-results" in self.content_lower
            or "vibe-sec handoff results" in self.content_lower
            or "vibe-sec-handoff" in self.content_lower
        )
        self.assertTrue(
            has_branch,
            "router/SKILL.md must declare a new state branch "
            "'review-vibe-sec-handoff-results'"
        )

    # ------------------------------------------------------------------ #
    # 2. Trigger references handoff-vibe-sec-*.json files                 #
    # ------------------------------------------------------------------ #

    def test_branch_triggers_on_handoff_result_file(self):
        has_trigger = (
            "handoff-vibe-sec-" in self.content
            or "handoff-vibe-sec-*.json" in self.content
            or "handoff-vibe-sec-<timestamp>.json" in self.content
            or "remediate/state/handoff-vibe-sec" in self.content
        )
        self.assertTrue(
            has_trigger,
            "Router branch must reference "
            ".vibe-prompt/remediate/state/handoff-vibe-sec-*.json as trigger"
        )

    # ------------------------------------------------------------------ #
    # 3. Branch surfaces vibe-sec findings from the handoff               #
    # ------------------------------------------------------------------ #

    def test_branch_surfaces_vibe_sec_findings(self):
        idx = self.content_lower.find("review-vibe-sec-handoff-results")
        if idx == -1:
            idx = self.content_lower.find("vibe-sec handoff results")
        self.assertGreater(idx, -1)
        section = self.content[idx:idx + 2000]
        has_finding_surface = (
            "vibesecfindings" in section.lower()
            or "vibe-sec finding" in section.lower()
            or "vibe-sec result" in section.lower()
            or "vibesecresultpath" in section.lower()
            or "exitcode" in section.lower()
        )
        self.assertTrue(
            has_finding_surface,
            "Router branch must surface vibe-sec findings from the handoff result"
        )

    # ------------------------------------------------------------------ #
    # 4. Branch label is named exactly                                    #
    # ------------------------------------------------------------------ #

    def test_branch_label_named(self):
        self.assertIn(
            "review-vibe-sec-handoff-results",
            self.content_lower,
            "Router must have a named branch 'review-vibe-sec-handoff-results'"
        )

    # ------------------------------------------------------------------ #
    # 5. Branch integrated into ## State checks                           #
    # ------------------------------------------------------------------ #

    def test_branch_integrated_in_state_checks(self):
        state_checks_idx = self.content.find("## State checks")
        self.assertGreater(
            state_checks_idx, -1,
            "Router must have a '## State checks' section"
        )
        state_checks_section = self.content[state_checks_idx:]
        has_handoff = (
            "review-vibe-sec-handoff-results" in state_checks_section.lower()
            or "handoff-vibe-sec" in state_checks_section
        )
        self.assertTrue(
            has_handoff,
            "review-vibe-sec-handoff-results branch must appear inside ## State checks"
        )

    # ------------------------------------------------------------------ #
    # 6. Prior v0.5 + v0.4 branches still present (no regression)          #
    # ------------------------------------------------------------------ #

    def test_v05_pending_remediations_branch_still_present(self):
        self.assertIn(
            "review-pending-remediations",
            self.content.lower(),
            "v0.5 review-pending-remediations branch must still be present"
        )

    def test_v04_inject_attack_branch_still_present(self):
        self.assertIn(
            "inject-attack",
            self.content.lower(),
            "v0.4 inject-attack branch must still be present"
        )

    def test_prior_state_check_anchors_still_present(self):
        prior = [
            "inventory.json",
            "audit.json",
            "run-*.json",
            "grade",
            "iterate",
            "remediate/pending",
        ]
        missing = [b for b in prior if b not in self.content]
        self.assertEqual(
            missing, [],
            f"Prior router branches missing: {missing}"
        )


if __name__ == "__main__":
    unittest.main()
