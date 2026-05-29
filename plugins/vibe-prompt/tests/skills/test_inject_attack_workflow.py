"""
Task 19 — TDD tests for inject-attack-eval-workflow.md.

Asserts:
  1. File exists at skills/eval/references/inject-attack-eval-workflow.md
  2. Required sections present: Cost estimation, User confirmation gate,
     Per-prompt execution, Per-fixture iteration, Judge call, Results aggregation
  3. Cost ceiling check present ($0.20 default from config)
  4. Cross-vendor execution pattern (prod vendor + Claude in-session baseline)
  5. injectAttackResults and injectAttackSummary referenced as output targets
  6. --auto flag for headless mode mentioned
  7. resistanceRate in aggregation output
  8. Cost estimation formula components (prompts × fixtures × judge-call-cost)
  9. costCeiling referenced from config
  10. vendorBreakdown in summary referenced
"""

import pathlib
import re
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
WORKFLOW_FILE = SKILLS_DIR / "eval" / "references" / "inject-attack-eval-workflow.md"

REQUIRED_SECTIONS = [
    "Cost estimation",
    "User confirmation gate",
    "Per-prompt execution",
    "Per-fixture iteration",
    "Judge call",
    "Results aggregation",
]


class TestInjectAttackWorkflowFileExists(unittest.TestCase):

    def test_file_exists(self):
        self.assertTrue(
            WORKFLOW_FILE.exists(),
            f"inject-attack-eval-workflow.md not found at {WORKFLOW_FILE}"
        )


class TestInjectAttackWorkflowContent(unittest.TestCase):

    def setUp(self):
        self.content = WORKFLOW_FILE.read_text(encoding="utf-8")
        self.content_lower = self.content.lower()

    # ------------------------------------------------------------------ #
    # 1. Required sections present                                         #
    # ------------------------------------------------------------------ #

    def test_cost_estimation_section(self):
        self.assertIn(
            "Cost estimation",
            self.content,
            "Workflow must have 'Cost estimation' section"
        )

    def test_user_confirmation_gate_section(self):
        self.assertIn(
            "User confirmation gate",
            self.content,
            "Workflow must have 'User confirmation gate' section"
        )

    def test_per_prompt_execution_section(self):
        self.assertIn(
            "Per-prompt execution",
            self.content,
            "Workflow must have 'Per-prompt execution' section"
        )

    def test_per_fixture_iteration_section(self):
        self.assertIn(
            "Per-fixture iteration",
            self.content,
            "Workflow must have 'Per-fixture iteration' section"
        )

    def test_judge_call_section(self):
        self.assertIn(
            "Judge call",
            self.content,
            "Workflow must have 'Judge call' section"
        )

    def test_results_aggregation_section(self):
        self.assertIn(
            "Results aggregation",
            self.content,
            "Workflow must have 'Results aggregation' section"
        )

    # ------------------------------------------------------------------ #
    # 2. Cost ceiling check ($0.20 default)                               #
    # ------------------------------------------------------------------ #

    def test_cost_ceiling_default_referenced(self):
        """Workflow must reference the $0.20 default cost ceiling."""
        self.assertTrue(
            "0.20" in self.content or "$0.20" in self.content,
            "Workflow must reference the $0.20 default cost ceiling from config"
        )

    def test_cost_ceiling_from_config(self):
        """costCeiling must be read from config, not hardcoded only."""
        self.assertTrue(
            "costCeiling" in self.content or "cost ceiling" in self.content_lower,
            "Workflow must reference costCeiling from config.eval.injectAttack"
        )

    # ------------------------------------------------------------------ #
    # 3. Cross-vendor execution pattern                                   #
    # ------------------------------------------------------------------ #

    def test_prod_vendor_execution(self):
        """Workflow must call the prod vendor."""
        self.assertTrue(
            "prod" in self.content_lower
            or "production" in self.content_lower
            or "gemini" in self.content_lower,
            "Workflow must document prod-vendor execution"
        )

    def test_in_session_baseline_execution(self):
        """Workflow must call the in-session Claude baseline."""
        self.assertTrue(
            "baseline" in self.content_lower
            or "in-session" in self.content_lower,
            "Workflow must document in-session Claude baseline execution"
        )

    def test_cross_vendor_comparison(self):
        """Workflow must compare prod vs baseline vendors."""
        has_compare = (
            "compare" in self.content_lower
            or "cross-vendor" in self.content_lower
            or "vendor" in self.content_lower
        )
        self.assertTrue(
            has_compare,
            "Workflow must include cross-vendor comparison step"
        )

    # ------------------------------------------------------------------ #
    # 4. Output targets referenced                                        #
    # ------------------------------------------------------------------ #

    def test_inject_attack_results_referenced(self):
        self.assertIn(
            "injectAttackResults",
            self.content,
            "Workflow must reference run-result.injectAttackResults as output target"
        )

    def test_inject_attack_summary_referenced(self):
        self.assertIn(
            "injectAttackSummary",
            self.content,
            "Workflow must reference run-result.injectAttackSummary as output target"
        )

    # ------------------------------------------------------------------ #
    # 5. --auto flag for headless mode                                    #
    # ------------------------------------------------------------------ #

    def test_auto_flag_mentioned(self):
        """Workflow must mention --auto flag for headless/CI execution."""
        self.assertIn(
            "--auto",
            self.content,
            "Workflow must mention --auto flag for headless mode (skips user confirmation)"
        )

    # ------------------------------------------------------------------ #
    # 6. resistanceRate in aggregation                                    #
    # ------------------------------------------------------------------ #

    def test_resistance_rate_in_aggregation(self):
        self.assertIn(
            "resistanceRate",
            self.content,
            "Workflow must output resistanceRate in injectAttackSummary"
        )

    # ------------------------------------------------------------------ #
    # 7. Cost estimation formula components                               #
    # ------------------------------------------------------------------ #

    def test_cost_formula_includes_fixtures(self):
        """Cost formula must factor in fixture count."""
        self.assertTrue(
            "fixture" in self.content_lower and (
                "×" in self.content or "*" in self.content or "per" in self.content_lower
            ),
            "Cost estimation formula must reference fixture count as a factor"
        )

    def test_cost_formula_judge_cost(self):
        """Cost formula must reference per-judge-call cost."""
        self.assertTrue(
            "0.001" in self.content or "judge" in self.content_lower,
            "Cost estimation must reference per-judge-call cost (~$0.001)"
        )

    # ------------------------------------------------------------------ #
    # 8. vendorBreakdown in summary                                       #
    # ------------------------------------------------------------------ #

    def test_vendor_breakdown_in_summary(self):
        self.assertIn(
            "vendorBreakdown",
            self.content,
            "injectAttackSummary must include vendorBreakdown field"
        )

    # ------------------------------------------------------------------ #
    # 9. successfulAttacks in summary                                     #
    # ------------------------------------------------------------------ #

    def test_successful_attacks_in_summary(self):
        self.assertIn(
            "successfulAttacks",
            self.content,
            "injectAttackSummary must include successfulAttacks count"
        )

    # ------------------------------------------------------------------ #
    # 10. Cost-meter increment mentioned                                  #
    # ------------------------------------------------------------------ #

    def test_cost_meter_tracking(self):
        """Workflow must mention running cost tracking (cost-meter increments)."""
        self.assertTrue(
            "cost" in self.content_lower and (
                "meter" in self.content_lower
                or "increment" in self.content_lower
                or "running" in self.content_lower
                or "track" in self.content_lower
                or "tally" in self.content_lower
            ),
            "Workflow must mention cost-meter/running-cost tracking per judge call"
        )


if __name__ == "__main__":
    unittest.main()
