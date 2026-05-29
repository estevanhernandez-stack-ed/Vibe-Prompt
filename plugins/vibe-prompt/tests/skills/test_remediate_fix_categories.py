"""
Task 16 — TDD tests for skills/remediate/references/fix-categories.md.

Asserts the file declares all three fix categories per spec §1b with
diff templates and default confidences.
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
FIX_CATEGORIES = SKILLS_DIR / "remediate" / "references" / "fix-categories.md"


class TestRemediateFixCategories(unittest.TestCase):

    def setUp(self):
        self.assertTrue(
            FIX_CATEGORIES.exists(),
            f"references/fix-categories.md must exist at {FIX_CATEGORIES}",
        )
        self.content = FIX_CATEGORIES.read_text(encoding="utf-8")
        self.lower = self.content.lower()

    # Category A
    def test_category_a_declared(self):
        self.assertIn("Category A", self.content)
        self.assertTrue(
            "composer-level" in self.lower or "composer level" in self.lower,
            "Category A must describe composer-level additions",
        )

    def test_category_a_targets_f9(self):
        idx = self.content.find("Category A")
        self.assertGreater(idx, -1)
        # F9 mention must appear in or near the Category A section (next 2000 chars)
        section = self.content[idx:idx + 3000]
        self.assertIn("F9", section, "Category A must reference F9 findings")

    def test_category_a_default_confidence_0_92(self):
        idx = self.content.find("Category A")
        section = self.content[idx:idx + 3000]
        self.assertIn("0.92", section, "Category A must declare 0.92 default confidence")

    def test_category_a_confidence_floor_0_80(self):
        idx = self.content.find("Category A")
        section = self.content[idx:idx + 3000]
        self.assertIn("0.80", section, "Category A must declare 0.80 confidence floor")

    def test_category_a_has_diff_template(self):
        idx = self.content.find("Category A")
        section = self.content[idx:idx + 3000]
        self.assertIn("CURRENT DATE", section, "Category A diff template must include [CURRENT DATE] block")
        self.assertIn("masterSystemInstruction", section, "Category A template references masterSystemInstruction")

    # Category B
    def test_category_b_declared(self):
        self.assertIn("Category B", self.content)
        self.assertTrue(
            "contradiction" in self.lower,
            "Category B must describe contradiction removal",
        )

    def test_category_b_targets_f2(self):
        idx = self.content.find("Category B")
        section = self.content[idx:idx + 3000]
        self.assertIn("F2", section, "Category B must reference F2 findings")

    def test_category_b_default_confidence_0_75(self):
        idx = self.content.find("Category B")
        section = self.content[idx:idx + 3000]
        self.assertIn("0.75", section, "Category B must declare 0.75 default confidence")

    def test_category_b_floor_0_50(self):
        idx = self.content.find("Category B")
        section = self.content[idx:idx + 3000]
        self.assertIn("0.50", section, "Category B must declare 0.50 confidence floor")

    def test_category_b_requires_opt_in(self):
        idx = self.content.find("Category B")
        section = self.content[idx:idx + 3000]
        self.assertIn("--apply-contradictions", section, "Category B must reference --apply-contradictions opt-in flag")

    # Category C
    def test_category_c_declared(self):
        self.assertIn("Category C", self.content)
        self.assertTrue(
            "defense" in self.lower,
            "Category C must describe defense addition",
        )

    def test_category_c_targets_f10_f11(self):
        idx = self.content.find("Category C")
        section = self.content[idx:idx + 3500]
        self.assertIn("F10", section)
        self.assertIn("F11", section)

    def test_category_c_contract_confidence_0_88(self):
        idx = self.content.find("Category C")
        section = self.content[idx:idx + 3500]
        self.assertIn("0.88", section, "Category C contract paragraph default confidence 0.88")

    def test_category_c_delimiter_confidence_0_78(self):
        idx = self.content.find("Category C")
        section = self.content[idx:idx + 3500]
        self.assertIn("0.78", section, "Category C delimiter placement default confidence 0.78")

    def test_category_c_has_interpretation_contract_template(self):
        idx = self.content.find("Category C")
        section = self.content[idx:idx + 3500]
        self.assertIn("INTERPRETATION CONTRACT", section)
        self.assertIn("DELIMITER", section)

    # F12 handling
    def test_f12_critical_does_not_propose(self):
        lower = self.content.lower()
        self.assertIn("f12", lower)
        self.assertTrue(
            "handoff" in lower or "does not propose" in lower or "do not propose" in lower,
            "fix-categories must document F12 critical = handoff, not proposal",
        )


if __name__ == "__main__":
    unittest.main()
