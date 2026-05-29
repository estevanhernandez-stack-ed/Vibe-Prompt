"""
Task 15 — TDD tests for skills/remediate/SKILL.md (main workflow).

Asserts the remediate SKILL file exists and declares the 8 workflow sections
per spec §1a:
  1. Read state
  2. Group findings by fix category
  3. Generate proposed diff + score confidence
  4. Route by confidence
  5. Present plan + user gate
  6. Apply or stage
  7. Post-apply guidance
  8. Friction-log
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
REMEDIATE_SKILL = SKILLS_DIR / "remediate" / "SKILL.md"


class TestRemediateWorkflow(unittest.TestCase):

    def setUp(self):
        self.assertTrue(
            REMEDIATE_SKILL.exists(),
            f"skills/remediate/SKILL.md must exist at {REMEDIATE_SKILL}",
        )
        self.content = REMEDIATE_SKILL.read_text(encoding="utf-8")

    def test_skill_has_frontmatter(self):
        self.assertTrue(
            self.content.startswith("---"),
            "remediate/SKILL.md must start with YAML front-matter",
        )

    def test_skill_name_is_vibe_prompt_remediate(self):
        self.assertIn(
            "name: vibe-prompt:remediate",
            self.content,
            "SKILL.md front-matter must declare name: vibe-prompt:remediate",
        )

    def test_workflow_step_read_state(self):
        # Step 1: Read state — load audit, run-result, inventory, composer.json
        lower = self.content.lower()
        self.assertTrue(
            "read state" in lower or "1. read" in lower or "load state" in lower,
            "Workflow must declare a 'Read state' step",
        )
        # Must mention loading audit.json, inventory.json, composer.json
        self.assertIn("audit.json", self.content)
        self.assertIn("inventory.json", self.content)
        self.assertIn("composer.json", self.content)

    def test_workflow_step_group_by_category(self):
        lower = self.content.lower()
        self.assertTrue(
            "group findings" in lower or "group by" in lower or "by fix category" in lower,
            "Workflow must declare a 'Group findings by category' step",
        )

    def test_workflow_step_generate_diff_and_score(self):
        lower = self.content.lower()
        self.assertTrue(
            "generate" in lower and "diff" in lower,
            "Workflow must declare generation of a proposed diff",
        )
        self.assertTrue(
            "score confidence" in lower or "confidence rubric" in lower or "score per the rubric" in lower,
            "Workflow must declare confidence scoring step",
        )

    def test_workflow_step_route_by_confidence(self):
        # ≥0.90 auto-write, 0.70-0.89 stage, <0.70 inline-only
        self.assertIn("auto-write", self.content.lower())
        self.assertIn("stage", self.content.lower())
        self.assertTrue(
            "inline-only" in self.content.lower() or "inline only" in self.content.lower(),
            "Workflow must reference inline-only routing for low-confidence diffs",
        )
        self.assertIn("0.90", self.content)
        self.assertIn("0.70", self.content)

    def test_workflow_step_present_plan_and_user_gate(self):
        lower = self.content.lower()
        self.assertTrue(
            "present plan" in lower or "summary banner" in lower or "user gate" in lower,
            "Workflow must declare a present-plan + user-gate step",
        )

    def test_workflow_step_apply_or_stage(self):
        lower = self.content.lower()
        self.assertTrue(
            "apply or stage" in lower or "apply" in lower and "stage" in lower,
            "Workflow must declare apply-or-stage step",
        )
        # Must mention backup + pending dir
        self.assertIn(".vibe-prompt/remediate/backup", self.content)
        self.assertIn(".vibe-prompt/remediate/pending", self.content)

    def test_workflow_step_post_apply_guidance(self):
        lower = self.content.lower()
        self.assertTrue(
            "post-apply" in lower or "post apply" in lower or "re-run" in lower,
            "Workflow must declare a post-apply guidance step (re-run eval)",
        )
        self.assertIn(":eval", self.content)

    def test_workflow_step_friction_log(self):
        lower = self.content.lower()
        self.assertTrue(
            "friction-log" in lower or "friction log" in lower,
            "Workflow must declare a friction-log step",
        )

    def test_skill_references_fix_categories(self):
        self.assertIn("fix-categories", self.content)

    def test_skill_references_confidence_rubric(self):
        self.assertIn("confidence-rubric", self.content)

    def test_skill_references_delimiter_naming(self):
        self.assertIn("delimiter-naming", self.content)

    def test_skill_references_diff_patch_helpers(self):
        self.assertIn("diff-patch-helpers", self.content)

    def test_skill_references_rollback_workflow(self):
        self.assertIn("rollback-workflow", self.content)


if __name__ == "__main__":
    unittest.main()
