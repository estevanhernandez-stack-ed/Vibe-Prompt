"""
Task 24 — TDD tests for the inject-attack state branch in router/SKILL.md.

New branch: "review-injection-attack-results"
Trigger: .vibe-prompt/eval/state/run-*.json has non-empty injectAttackResults array.

Asserts:
  1. router/SKILL.md declares a new state branch for inject-attack results
  2. Branch is triggered when injectAttackResults array is non-empty
  3. Branch presents the inject-attack summary to the user
  4. Branch offers next actions: review per-fixture results, dispatch evolve-prompt,
     run vibe-sec handoff
  5. The branch label / name references "inject-attack" or "injection-attack"
  6. The branch reads from .vibe-prompt/eval/state/run-*.json (correct path)
  7. The branch fits into the existing numbered state flow (doesn't break v0.3 branches)
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
ROUTER_SKILL = SKILLS_DIR / "router" / "SKILL.md"


class TestRouterV04InjectAttackBranch(unittest.TestCase):

    def setUp(self):
        self.content = ROUTER_SKILL.read_text(encoding="utf-8")
        self.content_lower = self.content.lower()

    # ------------------------------------------------------------------ #
    # 1. New inject-attack branch exists                                   #
    # ------------------------------------------------------------------ #

    def test_inject_attack_branch_declared(self):
        """Router must declare a branch for inject-attack results."""
        has_branch = (
            "inject-attack" in self.content_lower
            or "injectattack" in self.content_lower
            or "injection-attack" in self.content_lower
        )
        self.assertTrue(
            has_branch,
            "router/SKILL.md must declare a new state branch for inject-attack results"
        )

    # ------------------------------------------------------------------ #
    # 2. Trigger condition: non-empty injectAttackResults                 #
    # ------------------------------------------------------------------ #

    def test_branch_triggers_on_inject_attack_results(self):
        """Branch must trigger when injectAttackResults is non-empty."""
        has_trigger = (
            "injectAttackResults" in self.content
            or "inject-attack-results" in self.content_lower
            or "inject attack results" in self.content_lower
        )
        self.assertTrue(
            has_trigger,
            "Router branch must reference injectAttackResults as the trigger condition"
        )

    # ------------------------------------------------------------------ #
    # 3. Branch presents inject-attack summary                           #
    # ------------------------------------------------------------------ #

    def test_branch_presents_inject_attack_summary(self):
        """Branch must surface the inject-attack summary (successfulAttacks, resistanceRate)."""
        has_summary = (
            "injectAttackSummary" in self.content
            or "successfulAttacks" in self.content
            or "resistanceRate" in self.content
            or "attack summary" in self.content_lower
            or "inject-attack summary" in self.content_lower
        )
        self.assertTrue(
            has_summary,
            "Router branch must present the inject-attack summary to the user"
        )

    # ------------------------------------------------------------------ #
    # 4. Branch offers next actions                                       #
    # ------------------------------------------------------------------ #

    def test_branch_offers_evolve_prompt_next_action(self):
        """Branch must offer evolve-prompt as a next action."""
        # Find the inject-attack branch section
        inject_idx = self.content_lower.find("inject-attack")
        self.assertGreater(inject_idx, -1)
        branch_section = self.content[inject_idx:inject_idx + 1500]
        has_evolve = (
            "evolve-prompt" in branch_section.lower()
            or "evolve" in branch_section.lower()
        )
        self.assertTrue(
            has_evolve,
            "Router inject-attack branch must offer evolve-prompt as a next action"
        )

    def test_branch_offers_vibe_sec_handoff(self):
        """Branch must offer vibe-sec handoff as a next action."""
        inject_idx = self.content_lower.find("inject-attack")
        self.assertGreater(inject_idx, -1)
        branch_section = self.content[inject_idx:inject_idx + 1500]
        has_vibe_sec = (
            "vibe-sec" in branch_section.lower()
            or "security" in branch_section.lower()
            or "handoff" in branch_section.lower()
        )
        self.assertTrue(
            has_vibe_sec,
            "Router inject-attack branch must offer vibe-sec handoff as a next action"
        )

    # ------------------------------------------------------------------ #
    # 5. Branch label references inject-attack or injection-attack        #
    # ------------------------------------------------------------------ #

    def test_branch_label_named(self):
        """Branch should have a recognizable label referencing inject-attack."""
        has_label = (
            "review-injection-attack-results" in self.content_lower
            or "review inject-attack results" in self.content_lower
            or "inject-attack results" in self.content_lower
        )
        self.assertTrue(
            has_label,
            "Router must have a named branch like 'review-injection-attack-results'"
        )

    # ------------------------------------------------------------------ #
    # 6. Branch reads from correct path                                   #
    # ------------------------------------------------------------------ #

    def test_branch_reads_from_eval_state(self):
        """Branch must reference .vibe-prompt/eval/state/ path."""
        has_path = (
            "eval/state" in self.content
            or ".vibe-prompt/eval" in self.content
            or "run-*.json" in self.content
        )
        self.assertTrue(
            has_path,
            "Router branch must reference .vibe-prompt/eval/state/run-*.json as the state source"
        )

    # ------------------------------------------------------------------ #
    # 7. Existing v0.3 branches still present (no regression)            #
    # ------------------------------------------------------------------ #

    def test_v03_branches_still_present(self):
        """All v0.3 branches must still be present (no regression)."""
        v03_branches = [
            "inventory.json",   # Branch 1 trigger
            "audit.json",       # Branch 2 trigger
            "run-*.json",       # Branch 3 trigger (eval state)
            "grade",            # Branch 5
            "iterate",          # Branch 6
        ]
        missing = [b for b in v03_branches if b not in self.content]
        self.assertEqual(
            missing, [],
            f"v0.3 branches are missing from router: {missing}"
        )

    # ------------------------------------------------------------------ #
    # 8. Branch is integrated into the state-check flow                  #
    # ------------------------------------------------------------------ #

    def test_branch_integrated_in_state_checks(self):
        """The new branch must appear in the ## State checks section."""
        state_checks_idx = self.content.find("## State checks")
        self.assertGreater(
            state_checks_idx, -1,
            "Router must have a '## State checks' section"
        )
        state_checks_section = self.content[state_checks_idx:]
        has_inject = (
            "inject-attack" in state_checks_section.lower()
            or "injectAttackResults" in state_checks_section
        )
        self.assertTrue(
            has_inject,
            "inject-attack branch must appear inside the ## State checks section"
        )


if __name__ == "__main__":
    unittest.main()
