"""
Task 23 (v0.5) — TDD tests for the review-pending-remediations state branch in router/SKILL.md.

New branch: "review-pending-remediations"
Trigger: .vibe-prompt/remediate/pending/*.diff exists.

Asserts:
  1. router/SKILL.md declares a new state branch for pending remediations
  2. Branch is triggered when .vibe-prompt/remediate/pending/*.diff exists
  3. Branch surfaces the pending finding list
  4. Branch offers next actions: review per-finding, apply-pending, reject-pending
  5. The branch label references "review-pending-remediations"
  6. The branch fits into the existing numbered state flow (doesn't break v0.4 branches)
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
ROUTER_SKILL = SKILLS_DIR / "router" / "SKILL.md"


class TestRouterV05PendingRemediationsBranch(unittest.TestCase):

    def setUp(self):
        self.content = ROUTER_SKILL.read_text(encoding="utf-8")
        self.content_lower = self.content.lower()

    # ------------------------------------------------------------------ #
    # 1. Pending-remediations branch declared                             #
    # ------------------------------------------------------------------ #

    def test_pending_remediations_branch_declared(self):
        has_branch = (
            "review-pending-remediations" in self.content_lower
            or "pending remediations" in self.content_lower
            or "pending-remediation" in self.content_lower
        )
        self.assertTrue(
            has_branch,
            "router/SKILL.md must declare a new state branch for pending remediations"
        )

    # ------------------------------------------------------------------ #
    # 2. Trigger condition: pending/*.diff exists                          #
    # ------------------------------------------------------------------ #

    def test_branch_triggers_on_pending_diff(self):
        has_trigger = (
            "remediate/pending" in self.content
            or "remediate/pending/" in self.content
            or "*.diff" in self.content
            or "<finding-id>.diff" in self.content
        )
        self.assertTrue(
            has_trigger,
            "Router branch must reference .vibe-prompt/remediate/pending/*.diff as trigger"
        )

    # ------------------------------------------------------------------ #
    # 3. Branch surfaces the pending finding list                         #
    # ------------------------------------------------------------------ #

    def test_branch_surfaces_pending_finding_list(self):
        idx = self.content_lower.find("review-pending-remediations")
        if idx == -1:
            idx = self.content_lower.find("pending remediations")
        self.assertGreater(idx, -1)
        section = self.content[idx:idx + 1800]
        has_listing = (
            "finding" in section.lower()
            or "diff" in section.lower()
            or "category" in section.lower()
            or "pending" in section.lower()
        )
        self.assertTrue(
            has_listing,
            "Router branch must surface the list of pending finding diffs to the user"
        )

    # ------------------------------------------------------------------ #
    # 4. Branch offers apply-pending and reject-pending next actions      #
    # ------------------------------------------------------------------ #

    def test_branch_offers_apply_pending(self):
        idx = self.content_lower.find("review-pending-remediations")
        if idx == -1:
            idx = self.content_lower.find("pending remediations")
        self.assertGreater(idx, -1)
        section = self.content[idx:idx + 2000]
        has_apply = (
            "--apply-pending" in section
            or "apply-pending" in section
            or "apply pending" in section.lower()
        )
        self.assertTrue(
            has_apply,
            "Router branch must offer --apply-pending as a next action"
        )

    def test_branch_offers_reject_pending(self):
        idx = self.content_lower.find("review-pending-remediations")
        if idx == -1:
            idx = self.content_lower.find("pending remediations")
        self.assertGreater(idx, -1)
        section = self.content[idx:idx + 2000]
        has_reject = (
            "--reject-pending" in section
            or "reject-pending" in section
            or "reject pending" in section.lower()
        )
        self.assertTrue(
            has_reject,
            "Router branch must offer --reject-pending as a next action"
        )

    # ------------------------------------------------------------------ #
    # 5. Branch label is named                                            #
    # ------------------------------------------------------------------ #

    def test_branch_label_named(self):
        self.assertIn(
            "review-pending-remediations",
            self.content_lower,
            "Router must have a named branch 'review-pending-remediations'"
        )

    # ------------------------------------------------------------------ #
    # 6. Branch integrated into state checks                              #
    # ------------------------------------------------------------------ #

    def test_branch_integrated_in_state_checks(self):
        state_checks_idx = self.content.find("## State checks")
        self.assertGreater(
            state_checks_idx, -1,
            "Router must have a '## State checks' section"
        )
        state_checks_section = self.content[state_checks_idx:]
        has_pending = (
            "review-pending-remediations" in state_checks_section.lower()
            or "remediate/pending" in state_checks_section
        )
        self.assertTrue(
            has_pending,
            "review-pending-remediations branch must appear inside ## State checks"
        )

    # ------------------------------------------------------------------ #
    # 7. v0.4 inject-attack branch still present (no regression)          #
    # ------------------------------------------------------------------ #

    def test_v04_inject_attack_branch_still_present(self):
        self.assertIn(
            "inject-attack",
            self.content.lower(),
            "v0.4 inject-attack branch must still be present"
        )

    def test_v04_v03_branches_still_present(self):
        """All prior branches must still exist."""
        prior = [
            "inventory.json",
            "audit.json",
            "run-*.json",
            "grade",
            "iterate",
        ]
        missing = [b for b in prior if b not in self.content]
        self.assertEqual(
            missing, [],
            f"Prior router branches missing: {missing}"
        )


if __name__ == "__main__":
    unittest.main()
