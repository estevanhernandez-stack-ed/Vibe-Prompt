"""
Task 28 — TDD tests for skills/remediate/references/consolidation-rules.md.

Asserts the new v0.7 reference file exists and declares the consolidation
priority order + when-not-to-consolidate rules per spec §"F10+F11+F12
consolidated-diff routing".
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
CONSOLIDATION_RULES = (
    SKILLS_DIR / "remediate" / "references" / "consolidation-rules.md"
)


class TestConsolidationRulesReference(unittest.TestCase):

    def setUp(self):
        self.assertTrue(
            CONSOLIDATION_RULES.exists(),
            f"references/consolidation-rules.md must exist at {CONSOLIDATION_RULES}",
        )
        self.content = CONSOLIDATION_RULES.read_text(encoding="utf-8")
        self.lower = self.content.lower()

    def test_has_f10_f11_consolidation_section(self):
        self.assertIn(
            "F10 + F11 consolidation",
            self.content,
            "reference must declare 'F10 + F11 consolidation' section",
        )

    def test_has_f10_f11_f12_high_consolidation_section(self):
        self.assertIn(
            "F10 + F11 + F12-high consolidation",
            self.content,
            "reference must declare 'F10 + F11 + F12-high consolidation' section",
        )

    def test_has_priority_order_section(self):
        self.assertIn(
            "Priority order",
            self.content,
            "reference must declare 'Priority order' section",
        )

    def test_has_when_not_to_consolidate_section(self):
        self.assertIn(
            "When NOT to consolidate",
            self.content,
            "reference must declare 'When NOT to consolidate' section",
        )

    def test_priority_documents_f10_as_structural(self):
        # Priority order: F10 defense block is the structural change
        idx = self.content.find("Priority order")
        section = self.content[idx:idx + 2000].lower()
        self.assertIn(
            "structural",
            section,
            "Priority order must document F10 defense block as the structural change",
        )
        self.assertIn(
            "f10",
            section,
            "Priority order must reference F10",
        )

    def test_priority_documents_f11_satisfied_by_f10(self):
        idx = self.content.find("Priority order")
        section = self.content[idx:idx + 2000].lower()
        self.assertTrue(
            "f11" in section and ("satisfied" in section or "phrase count" in section or "satisfies" in section),
            "Priority order must document F11 phrase count satisfied by F10's contract",
        )

    def test_priority_documents_f12_high_comment(self):
        idx = self.content.find("Priority order")
        section = self.content[idx:idx + 2000].lower()
        self.assertTrue(
            "f12" in section and ("comment" in section or "deferral" in section or "deferred" in section),
            "Priority order must document F12-high comment about composition restructure deferral",
        )

    def test_not_to_consolidate_different_call_sites(self):
        idx = self.content.find("When NOT to consolidate")
        section = self.content[idx:idx + 2000].lower()
        self.assertTrue(
            "call site" in section or "call-site" in section,
            "When-NOT-to-consolidate must document different call sites",
        )

    def test_not_to_consolidate_f12_critical(self):
        idx = self.content.find("When NOT to consolidate")
        section = self.content[idx:idx + 2000]
        self.assertIn(
            "F12-critical",
            section,
            "When-NOT-to-consolidate must document F12-critical exclusion",
        )

    def test_not_to_consolidate_references_auto_handoff(self):
        idx = self.content.find("When NOT to consolidate")
        section = self.content[idx:idx + 2000].lower()
        self.assertTrue(
            "auto-handoff" in section or "handoff" in section,
            "When-NOT-to-consolidate must reference auto-handoff path for F12-critical",
        )


if __name__ == "__main__":
    unittest.main()
