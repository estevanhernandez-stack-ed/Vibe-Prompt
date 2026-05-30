"""
Task 17 — TDD tests for Category B sub-category split (banned-phrase vs
voice-frame) in fix-categories.md + remediate/SKILL.md.

Asserts:
- fix-categories.md declares the two sub-categories with their confidence + routing
- banned-phrase-removal: confidence 0.75, follows v0.5 default routing
- voice-frame-rewrite: confidence 0.65, ALWAYS stages by default (auto-write
  requires --apply-voice-frame-fixes opt-in)
- SKILL.md emits subCategory field on diffs
- Both can fire on the same prompt (separate diffs)
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
FIX_CATEGORIES = SKILLS_DIR / "remediate" / "references" / "fix-categories.md"
REMEDIATE_SKILL = SKILLS_DIR / "remediate" / "SKILL.md"


class TestCategoryBSubCategory(unittest.TestCase):

    def setUp(self):
        self.fix_categories = FIX_CATEGORIES.read_text(encoding="utf-8")
        self.skill = REMEDIATE_SKILL.read_text(encoding="utf-8")

    # --- fix-categories.md declarations ---
    def test_subcategory_banned_phrase_removal_declared(self):
        self.assertIn(
            "banned-phrase-removal",
            self.fix_categories,
            "fix-categories.md must declare `banned-phrase-removal` sub-category",
        )

    def test_subcategory_voice_frame_rewrite_declared(self):
        self.assertIn(
            "voice-frame-rewrite",
            self.fix_categories,
            "fix-categories.md must declare `voice-frame-rewrite` sub-category",
        )

    def test_banned_phrase_confidence_0_75(self):
        # Banned-phrase removal at 0.75 (v0.5 carry-over)
        idx = self.fix_categories.find("banned-phrase-removal")
        self.assertGreater(idx, -1)
        section = self.fix_categories[max(0, idx - 200):idx + 600]
        self.assertIn(
            "0.75",
            section,
            "banned-phrase-removal confidence must be 0.75 per spec §5",
        )

    def test_voice_frame_confidence_0_65(self):
        idx = self.fix_categories.find("voice-frame-rewrite")
        self.assertGreater(idx, -1)
        section = self.fix_categories[max(0, idx - 200):idx + 800]
        self.assertIn(
            "0.65",
            section,
            "voice-frame-rewrite confidence must be 0.65 per spec §5",
        )

    def test_voice_frame_always_stages(self):
        idx = self.fix_categories.find("voice-frame-rewrite")
        self.assertGreater(idx, -1)
        section = self.fix_categories[idx:idx + 1500].lower()
        # ALWAYS stages by default — no auto-write without flag
        self.assertTrue(
            "always stage" in section
            or "always-stage" in section
            or "stages by default" in section
            or "stage by default" in section,
            "voice-frame-rewrite must ALWAYS stage by default",
        )

    def test_voice_frame_references_apply_voice_frame_fixes_flag(self):
        idx = self.fix_categories.find("voice-frame-rewrite")
        self.assertGreater(idx, -1)
        section = self.fix_categories[idx:idx + 1500]
        self.assertIn(
            "--apply-voice-frame-fixes",
            section,
            "voice-frame-rewrite must reference --apply-voice-frame-fixes opt-in flag",
        )

    # --- SKILL.md emits subCategory ---
    def test_skill_emits_subcategory_field(self):
        self.assertIn(
            "subCategory",
            self.skill,
            "remediate/SKILL.md must emit subCategory field on Category B diffs",
        )

    def test_skill_distinguishes_banned_phrase_vs_voice_frame(self):
        self.assertIn("banned-phrase-removal", self.skill)
        self.assertIn("voice-frame-rewrite", self.skill)

    def test_skill_documents_both_can_fire_on_same_prompt(self):
        # The two sub-categories can produce separate diffs on the same prompt
        lower = self.skill.lower()
        self.assertTrue(
            "separate diff" in lower
            or "two diffs" in lower
            or "independent diff" in lower
            or "same prompt" in lower,
            "SKILL.md must document that banned-phrase + voice-frame can coexist on a prompt",
        )


if __name__ == "__main__":
    unittest.main()
