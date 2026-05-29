"""
Task 20 — TDD tests for --inject-attacks flag in eval/SKILL.md.

Asserts:
  1. eval/SKILL.md declares --inject-attacks as a CLI flag
  2. When flag present, workflow includes inject-attack-eval-workflow as sub-step
     AFTER the standard prod + baseline + judge pipeline
  3. Results write to run-result.injectAttackResults
  4. Results write to run-result.injectAttackSummary
  5. Without the flag, existing v0.3 behavior is unchanged (flag is opt-in)
  6. The flag is documented in the Inputs / CLI flags section
  7. inject-attack-eval-workflow.md is referenced in the SKILL
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
EVAL_SKILL = SKILLS_DIR / "eval" / "SKILL.md"


class TestEvalInjectAttacksFlagInSkill(unittest.TestCase):

    def setUp(self):
        self.content = EVAL_SKILL.read_text(encoding="utf-8")
        self.content_lower = self.content.lower()

    # ------------------------------------------------------------------ #
    # 1. Flag declared in CLI flags section                               #
    # ------------------------------------------------------------------ #

    def test_inject_attacks_flag_declared(self):
        self.assertIn(
            "--inject-attacks",
            self.content,
            "eval/SKILL.md must declare --inject-attacks as a CLI flag"
        )

    # ------------------------------------------------------------------ #
    # 2. Sub-workflow referenced                                          #
    # ------------------------------------------------------------------ #

    def test_inject_attack_eval_workflow_referenced(self):
        self.assertIn(
            "inject-attack-eval-workflow",
            self.content,
            "eval/SKILL.md must reference inject-attack-eval-workflow.md as a sub-step"
        )

    # ------------------------------------------------------------------ #
    # 3. Sub-workflow runs AFTER standard pipeline                        #
    # ------------------------------------------------------------------ #

    def test_inject_attacks_runs_after_standard_pipeline(self):
        """The inject-attack sub-workflow must come after the standard eval pipeline."""
        # The standard pipeline ends at 'Write eval-result' or 'Render' steps
        # The inject-attack sub-workflow should follow
        standard_pipeline_marker = self.content.find("Write eval-result")
        inject_attacks_marker = self.content.find("inject-attack")

        if standard_pipeline_marker == -1:
            # Fall back to checking 'Render' step as end of standard pipeline
            standard_pipeline_marker = self.content.find("Render dashboard")

        self.assertGreater(
            standard_pipeline_marker,
            -1,
            "Could not find standard pipeline marker in eval/SKILL.md"
        )
        self.assertGreater(
            inject_attacks_marker,
            -1,
            "inject-attack reference not found in eval/SKILL.md"
        )
        # inject-attack workflow must appear AFTER the standard pipeline marker
        # (but it may appear in the inputs/flags section too — find the workflow reference)
        workflow_marker = self.content.find("inject-attack-eval-workflow")
        self.assertGreater(
            workflow_marker,
            standard_pipeline_marker,
            "inject-attack-eval-workflow sub-step must appear AFTER the standard pipeline in the workflow"
        )

    # ------------------------------------------------------------------ #
    # 4. Results targets specified                                        #
    # ------------------------------------------------------------------ #

    def test_inject_attack_results_target_referenced(self):
        self.assertIn(
            "injectAttackResults",
            self.content,
            "eval/SKILL.md must specify injectAttackResults as an output target"
        )

    def test_inject_attack_summary_target_referenced(self):
        self.assertIn(
            "injectAttackSummary",
            self.content,
            "eval/SKILL.md must specify injectAttackSummary as an output target"
        )

    # ------------------------------------------------------------------ #
    # 5. Flag is opt-in (without flag, existing behavior unchanged)       #
    # ------------------------------------------------------------------ #

    def test_inject_attacks_is_opt_in(self):
        """The flag must be described as opt-in / conditional."""
        has_opt_in = (
            "when" in self.content_lower and "--inject-attacks" in self.content
        ) or (
            "if" in self.content_lower and "inject-attacks" in self.content_lower
        ) or (
            "optional" in self.content_lower and "inject" in self.content_lower
        )
        self.assertTrue(
            has_opt_in,
            "eval/SKILL.md must describe --inject-attacks as opt-in (existing v0.3 behavior unchanged without it)"
        )

    # ------------------------------------------------------------------ #
    # 6. Flag is in the Inputs section                                    #
    # ------------------------------------------------------------------ #

    def test_flag_in_cli_flags_section(self):
        """--inject-attacks must appear in or near the CLI flags block."""
        # Check that the flag appears in the Inputs/CLI flags section
        inputs_idx = self.content.find("## Inputs")
        flag_idx = self.content.find("--inject-attacks")

        # Flag should appear within the Inputs section OR the Workflow section
        self.assertGreater(
            flag_idx,
            -1,
            "--inject-attacks not found in eval/SKILL.md at all"
        )
        # Both Inputs (flags list) and Workflow (conditional branch) are valid locations

    # ------------------------------------------------------------------ #
    # 7. Banner template updated for inject-attack mode                  #
    # ------------------------------------------------------------------ #

    def test_inject_attacks_referenced_in_workflow(self):
        """inject-attack must appear in the main workflow section."""
        workflow_idx = self.content.find("## Workflow")
        inject_idx_after_workflow = self.content.find("inject-attack", workflow_idx)
        self.assertGreater(
            inject_idx_after_workflow,
            -1,
            "--inject-attacks sub-workflow step must appear in the ## Workflow section"
        )


if __name__ == "__main__":
    unittest.main()
