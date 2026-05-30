"""
Task 20 — TDD tests for vibe-sec invocation workflow in remediate/SKILL.md.

Asserts:
- When --auto-handoff-vibe-sec flag set + F12 critical fires + vibe-sec
  installed:
    - SKILL workflow invokes vibe-sec:audit via the Skill tool
    - Passes --scope user-input-boundary argument (with fallback to full audit)
    - Captures vibe-sec exit code + findings
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
REMEDIATE_SKILL = SKILLS_DIR / "remediate" / "SKILL.md"


class TestVibeSecInvocationWorkflow(unittest.TestCase):

    def setUp(self):
        self.skill = REMEDIATE_SKILL.read_text(encoding="utf-8")
        self.lower = self.skill.lower()

    def test_skill_references_vibe_sec_audit_skill(self):
        # Must reference vibe-sec:audit specifically (the Skill being invoked)
        self.assertIn(
            "vibe-sec:audit",
            self.skill,
            "SKILL.md must reference vibe-sec:audit Skill invocation",
        )

    def test_skill_invokes_via_skill_tool(self):
        # Invocation uses the Skill tool (not direct shell exec)
        self.assertTrue(
            "skill tool" in self.lower
            or "via the skill tool" in self.lower
            or "via skill tool" in self.lower
            or "skill-tool" in self.lower,
            "SKILL.md must specify Skill tool as the invocation pattern",
        )

    def test_skill_passes_user_input_boundary_scope(self):
        self.assertIn(
            "user-input-boundary",
            self.skill,
            "SKILL.md must pass --scope user-input-boundary to vibe-sec",
        )

    def test_skill_fallback_to_full_audit(self):
        # If vibe-sec doesn't accept the scope flag, fall back to full audit
        self.assertTrue(
            "fallback" in self.lower or "full audit" in self.lower,
            "SKILL.md must document fallback to full audit when scope unsupported",
        )

    def test_skill_captures_exit_code(self):
        self.assertIn(
            "exit code",
            self.lower,
            "SKILL.md must document capturing vibe-sec exit code",
        )

    def test_skill_captures_findings(self):
        # Findings flow back into the handoff result file
        idx = self.lower.find("vibe-sec")
        section = self.lower[idx:idx + 4000]
        self.assertIn(
            "findings",
            section,
            "SKILL.md must document capturing vibe-sec findings",
        )

    def test_skill_documents_auto_handoff_workflow_branch(self):
        # SKILL.md must have a clearly-marked auto-handoff workflow branch
        self.assertTrue(
            "auto-handoff" in self.lower,
            "SKILL.md must document the auto-handoff workflow branch",
        )

    def test_skill_workflow_branch_conditional_on_flag_and_f12_critical(self):
        # The workflow branches when BOTH conditions are met
        # (flag set AND F12 critical fires)
        idx = self.lower.find("auto-handoff")
        self.assertGreater(idx, -1)
        section = self.lower[idx:idx + 3000]
        self.assertIn(
            "f12",
            section,
            "auto-handoff workflow must condition on F12 critical",
        )
        self.assertTrue(
            "critical" in section,
            "auto-handoff workflow must condition on F12 critical (severity)",
        )


if __name__ == "__main__":
    unittest.main()
