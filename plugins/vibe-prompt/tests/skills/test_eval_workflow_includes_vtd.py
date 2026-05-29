"""
Task 10 — TDD tests for value-type-drift wiring in eval/SKILL.md.

Asserts:
  1. eval/SKILL.md mechanical comparator step explicitly mentions value-type-drift
  2. The mention is between schema-shape and length-delta references in the workflow
  3. The mechanical check list calls out value-type-drift in the workflow step
  4. The reference to mechanical-comparator.md still exists (load reference intact)
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
EVAL_SKILL = SKILLS_DIR / "eval" / "SKILL.md"


class TestEvalWorkflowIncludesValueTypeDrift(unittest.TestCase):

    def setUp(self):
        self.content = EVAL_SKILL.read_text(encoding="utf-8")

    # ------------------------------------------------------------------ #
    # 1. value-type-drift mentioned in eval SKILL                         #
    # ------------------------------------------------------------------ #

    def test_value_type_drift_mentioned_in_eval_skill(self):
        self.assertIn(
            "value-type-drift",
            self.content,
            "eval/SKILL.md must mention value-type-drift in the mechanical workflow step"
        )

    # ------------------------------------------------------------------ #
    # 2. Reference to mechanical-comparator.md intact                     #
    # ------------------------------------------------------------------ #

    def test_mechanical_comparator_reference_intact(self):
        self.assertIn(
            "mechanical-comparator.md",
            self.content,
            "eval/SKILL.md must reference mechanical-comparator.md"
        )

    # ------------------------------------------------------------------ #
    # 3. Mechanical step in workflow calls out value-type-drift            #
    # ------------------------------------------------------------------ #

    def test_mechanical_comparator_step_includes_vtd(self):
        """The execute-eval step that runs mechanical comparator must mention value-type-drift."""
        # Find the WORKFLOW section first, then find the mechanical comparator reference within it
        workflow_idx = self.content.find("## Workflow")
        self.assertGreater(workflow_idx, -1, "## Workflow section not found in eval/SKILL.md")

        workflow_text = self.content[workflow_idx:]
        comp_ref_idx = workflow_text.find("mechanical-comparator")
        self.assertGreater(comp_ref_idx, -1, "mechanical-comparator reference not found in workflow section")

        # Check 2000 chars from the workflow section mechanical-comparator reference
        window = workflow_text[comp_ref_idx : comp_ref_idx + 2000]

        self.assertIn(
            "value-type-drift",
            window,
            "value-type-drift must be called out near the mechanical-comparator workflow step"
        )

    # ------------------------------------------------------------------ #
    # 4. Existing v0.3 workflow steps not removed                         #
    # ------------------------------------------------------------------ #

    def test_schema_shape_check_still_mentioned(self):
        self.assertIn(
            "schema-shape",
            self.content,
            "schema-shape must still be present in eval/SKILL.md"
        )

    def test_swap_and_discard_still_present(self):
        self.assertIn(
            "Swap-and-Discard",
            self.content,
            "Swap-and-Discard step must still be in eval/SKILL.md"
        )

    def test_cost_estimate_step_still_present(self):
        self.assertIn(
            "Cost estimate",
            self.content,
            "Cost estimate step must still be in eval/SKILL.md"
        )


if __name__ == "__main__":
    unittest.main()
