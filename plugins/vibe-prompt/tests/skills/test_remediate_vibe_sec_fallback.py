"""
Task 22 — TDD tests for vibe-sec availability check + graceful fallback in
remediate/SKILL.md.

Asserts:
- When --auto-handoff-vibe-sec set BUT vibe-sec not installed:
    - SKILL workflow detects unavailability via Skill tool absence
    - Falls back to v0.5 banner-only behavior
    - Friction-logs auto-handoff-vibe-sec-unavailable (medium)
    - Does NOT block the rest of :remediate run
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
REMEDIATE_SKILL = SKILLS_DIR / "remediate" / "SKILL.md"


class TestVibeSecFallback(unittest.TestCase):

    def setUp(self):
        self.skill = REMEDIATE_SKILL.read_text(encoding="utf-8")
        self.lower = self.skill.lower()

    def test_skill_documents_availability_check(self):
        # Skill tool registry lookup
        self.assertTrue(
            "availability check" in self.lower
            or "availability lookup" in self.lower
            or "available" in self.lower,
            "SKILL.md must document availability check for vibe-sec",
        )

    def test_skill_uses_skill_tool_for_availability(self):
        # The check must use the Skill tool's registry, NOT shell exec
        self.assertTrue(
            "skill tool" in self.lower
            or "skill-tool" in self.lower,
            "SKILL.md must specify Skill tool as the availability lookup channel",
        )

    def test_skill_documents_fallback_to_banner_only(self):
        self.assertTrue(
            "banner-only" in self.lower or "banner only" in self.lower,
            "SKILL.md must document fallback to v0.5 banner-only behavior",
        )

    def test_skill_friction_logs_unavailable(self):
        self.assertIn(
            "auto-handoff-vibe-sec-unavailable",
            self.skill,
            "SKILL.md must friction-log auto-handoff-vibe-sec-unavailable",
        )

    def test_friction_log_severity_is_medium(self):
        # The friction-trigger registration must classify as medium
        idx = self.skill.find("auto-handoff-vibe-sec-unavailable")
        self.assertGreater(idx, -1)
        section = self.skill[max(0, idx - 200):idx + 500].lower()
        self.assertIn(
            "medium",
            section,
            "auto-handoff-vibe-sec-unavailable must be tagged medium severity",
        )

    def test_skill_does_not_block_rest_of_remediate(self):
        # Documented as non-blocking — :remediate continues with v0.5 banner
        self.assertTrue(
            "do not block" in self.lower
            or "does not block" in self.lower
            or "not block" in self.lower
            or "continues" in self.lower,
            "SKILL.md must explicitly document non-blocking fallback",
        )

    def test_skill_documents_invocation_throw_also_falls_back(self):
        # When the Skill invocation itself throws, also fall back to banner
        lower = self.lower
        # Either "throw" or "invocation error" or "skill error"
        self.assertTrue(
            "throw" in lower or "skill error" in lower or "invocation" in lower,
            "SKILL.md must document the invocation-throw fallback path",
        )

    def test_skill_emits_one_line_notice_on_banner(self):
        # User must know fallback was taken (not silent)
        lower = self.lower
        self.assertTrue(
            "notice" in lower or "explain" in lower or "one-line" in lower,
            "SKILL.md must document the user-facing notice when fallback fires",
        )


if __name__ == "__main__":
    unittest.main()
