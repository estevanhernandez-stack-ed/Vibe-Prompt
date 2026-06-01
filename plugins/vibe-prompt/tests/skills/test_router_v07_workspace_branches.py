"""
Task 33 (v0.7) — TDD tests for the three new workspace + Category D state
branches in router/SKILL.md.

New branches:
  1. workspace-rescan-needed
       Trigger: inventory.json.workspaceKind === "npm-workspaces" OR
                "nested-projects" AND no per-workspace inventory files exist.
       Recommendation: /vibe-prompt:scan to populate workspace inventories.

  2. workspace-grade-needed
       Trigger: per-workspace inventories exist BUT no per-workspace grade
                results.
       Recommendation: /vibe-prompt:grade.

  3. category-d-pending-review
       Trigger: pending Category D diffs exist
                (`.vibe-prompt/remediate/pending/D-*.diff`).
       Recommendation: :remediate --apply-* flag hints in the next-step
                       recommendation banner.

Asserts:
  1. router/SKILL.md declares all three new branches.
  2. Each branch references its trigger condition explicitly.
  3. Each branch suggests its respective next-step skill / flag.
  4. Bare router state branches now sum to 13 (10 + 3 new).
  5. Prior v0.4/v0.5/v0.6 branches still present (no regression).
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
ROUTER_SKILL = SKILLS_DIR / "router" / "SKILL.md"


V07_BRANCHES = [
    "workspace-rescan-needed",
    "workspace-grade-needed",
    "category-d-pending-review",
]


class TestRouterV07WorkspaceBranches(unittest.TestCase):

    def setUp(self):
        self.content = ROUTER_SKILL.read_text(encoding="utf-8")
        self.content_lower = self.content.lower()

    # ------------------------------------------------------------------ #
    # 1. Three v0.7 branches declared                                     #
    # ------------------------------------------------------------------ #

    def test_all_v07_branches_declared(self):
        missing = [
            b for b in V07_BRANCHES if b not in self.content_lower
        ]
        self.assertEqual(
            missing, [],
            f"router/SKILL.md must declare v0.7 branches: missing {missing}"
        )

    # ------------------------------------------------------------------ #
    # 2. workspace-rescan-needed: triggers on workspaceKind + missing      #
    #    per-workspace inventory files                                    #
    # ------------------------------------------------------------------ #

    def test_workspace_rescan_branch_trigger(self):
        idx = self.content_lower.find("workspace-rescan-needed")
        self.assertGreater(idx, -1)
        section = self.content[idx:idx + 1500]
        section_lower = section.lower()
        has_workspace_kind = (
            "workspacekind" in section_lower
            or "workspace kind" in section_lower
            or "npm-workspaces" in section_lower
            or "nested-projects" in section_lower
        )
        self.assertTrue(
            has_workspace_kind,
            "workspace-rescan-needed branch must reference workspaceKind "
            "= npm-workspaces / nested-projects"
        )
        has_inventory_ref = (
            "inventory-" in section_lower
            or "per-workspace inventor" in section_lower
            or "inventory file" in section_lower
        )
        self.assertTrue(
            has_inventory_ref,
            "workspace-rescan-needed branch must reference missing "
            "per-workspace inventory files"
        )
        self.assertIn(
            "/vibe-prompt:scan", section,
            "workspace-rescan-needed branch must recommend /vibe-prompt:scan"
        )

    # ------------------------------------------------------------------ #
    # 3. workspace-grade-needed: triggers on per-workspace inventories     #
    #    but no per-workspace grade results                                #
    # ------------------------------------------------------------------ #

    def test_workspace_grade_branch_trigger(self):
        idx = self.content_lower.find("workspace-grade-needed")
        self.assertGreater(idx, -1)
        section = self.content[idx:idx + 1500]
        section_lower = section.lower()
        has_inventory_present = (
            "per-workspace inventor" in section_lower
            or "inventory-" in section_lower
            or "workspaces[]" in section
        )
        self.assertTrue(
            has_inventory_present,
            "workspace-grade-needed branch must reference existing "
            "per-workspace inventory artifacts"
        )
        self.assertIn(
            "/vibe-prompt:grade", section,
            "workspace-grade-needed branch must recommend /vibe-prompt:grade"
        )

    # ------------------------------------------------------------------ #
    # 4. category-d-pending-review: triggers on Category D pending diffs   #
    #    + recommends :remediate --apply-* flag                            #
    # ------------------------------------------------------------------ #

    def test_category_d_pending_branch_trigger(self):
        idx = self.content_lower.find("category-d-pending-review")
        self.assertGreater(idx, -1)
        section = self.content[idx:idx + 2000]
        has_pending_dir = (
            "remediate/pending" in section
            or "D-1" in section
            or "D-2" in section
            or "D-3" in section
            or "Category D" in section
        )
        self.assertTrue(
            has_pending_dir,
            "category-d-pending-review branch must reference Category D "
            "pending diffs"
        )
        has_apply_flag = (
            "--apply-inline-to-registry" in section
            or "--apply-typed-renderer" in section
            or "--apply-model-consolidation" in section
            or "--apply-" in section
        )
        self.assertTrue(
            has_apply_flag,
            "category-d-pending-review branch must mention at least one "
            "--apply-* flag hint for Category D"
        )

    # ------------------------------------------------------------------ #
    # 5. Branches integrated inside ## State checks                        #
    # ------------------------------------------------------------------ #

    def test_branches_integrated_in_state_checks(self):
        state_checks_idx = self.content.find("## State checks")
        self.assertGreater(state_checks_idx, -1)
        state_section = self.content[state_checks_idx:]
        state_section_lower = state_section.lower()
        missing = [
            b for b in V07_BRANCHES
            if b not in state_section_lower
        ]
        self.assertEqual(
            missing, [],
            f"v0.7 branches missing from ## State checks: {missing}"
        )

    # ------------------------------------------------------------------ #
    # 6. Total numbered state-check branches sum to >= 13 (10 + 3 new)     #
    # ------------------------------------------------------------------ #

    def test_total_branch_count_at_least_13(self):
        """The router should now have at least 13 distinct state branches.

        We count by anchoring on the named branches that exist (numbered + lettered).
        """
        # Prior 10 anchors (router pre-v0.7):
        prior_anchors = [
            "no `.vibe-prompt/state/inventory.json`",  # branch 1
            "no `.vibe-prompt/state/audit.json`",       # branch 2
            "eval pending",                              # branch 3
            "review-injection-attack-results",           # branch 3b
            "review-pending-remediations",               # branch 3c
            "review-vibe-sec-handoff-results",           # branch 3d
            "radar cache",                                # branch 4
            "grade pending",                              # branch 5
            "iterate pending",                            # branch 6
            "all fresh",                                  # branch 7 (case-insensitive)
        ]
        prior_count = sum(
            1 for a in prior_anchors
            if a.lower() in self.content_lower
        )
        new_count = sum(
            1 for b in V07_BRANCHES
            if b in self.content_lower
        )
        total = prior_count + new_count
        self.assertGreaterEqual(
            total, 13,
            f"Total state branches should be >= 13, found {total} "
            f"(prior={prior_count}, new={new_count})"
        )

    # ------------------------------------------------------------------ #
    # 7. Prior branches still present (no regression)                     #
    # ------------------------------------------------------------------ #

    def test_v06_handoff_branch_still_present(self):
        self.assertIn(
            "review-vibe-sec-handoff-results",
            self.content_lower,
            "v0.6 review-vibe-sec-handoff-results branch must still be present"
        )

    def test_v05_pending_branch_still_present(self):
        self.assertIn(
            "review-pending-remediations",
            self.content_lower,
            "v0.5 review-pending-remediations branch must still be present"
        )

    def test_v04_inject_branch_still_present(self):
        self.assertIn(
            "inject-attack",
            self.content_lower,
            "v0.4 inject-attack branch must still be present"
        )

    def test_prior_state_check_anchors_still_present(self):
        prior = [
            "inventory.json",
            "audit.json",
            "grade",
            "iterate",
            "remediate/pending",
        ]
        missing = [a for a in prior if a not in self.content]
        self.assertEqual(
            missing, [],
            f"Prior router anchors missing: {missing}"
        )


if __name__ == "__main__":
    unittest.main()
