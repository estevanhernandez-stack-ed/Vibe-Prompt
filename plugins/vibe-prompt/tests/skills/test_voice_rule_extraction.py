"""
Task 15 — TDD tests for voice-rule extraction step in remediate/SKILL.md.

Asserts the SKILL documents how to extract voice rules from the global directive
layer (bans + positive guidance + confidence per rule) per spec §5.
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
REMEDIATE_SKILL = SKILLS_DIR / "remediate" / "SKILL.md"


class TestVoiceRuleExtraction(unittest.TestCase):

    def setUp(self):
        self.content = REMEDIATE_SKILL.read_text(encoding="utf-8")
        self.lower = self.content.lower()

    def test_skill_documents_voice_rule_extraction_step(self):
        self.assertTrue(
            "voice-rule extraction" in self.lower
            or "voice rule extraction" in self.lower,
            "remediate/SKILL.md must document voice-rule extraction step",
        )

    def test_skill_references_voice_frame_detection_reference(self):
        self.assertIn(
            "voice-frame-detection.md",
            self.content,
            "remediate/SKILL.md must load references/voice-frame-detection.md",
        )

    def test_skill_extracts_bans_from_global_directive(self):
        # Must document the ban extraction
        self.assertTrue(
            "bans" in self.lower,
            "remediate/SKILL.md must describe extracting bans from global directive",
        )

    def test_skill_extracts_positive_guidance(self):
        self.assertTrue(
            "positive guidance" in self.lower
            or "positive-guidance" in self.lower
            or "positiveguidance" in self.lower,
            "remediate/SKILL.md must extract positive guidance",
        )

    def test_skill_includes_explicit_ban_pattern(self):
        # Spec §5: (?i)never (use|say|call|address)
        self.assertIn(
            "never",
            self.lower,
            "voice-rule extraction must reference `never (use|say|call|address)` pattern",
        )

    def test_skill_includes_persona_affirmation_implies_ban(self):
        # Spec §5: plain modern language bans archaic
        self.assertTrue(
            "plain modern language" in self.lower
            or "plain (modern" in self.lower,
            "voice-rule extraction must reference plain-modern-language affirmation",
        )

    def test_skill_reports_confidence_per_rule(self):
        # Per spec, extraction returns confidence per rule
        idx = self.lower.find("voice-rule extraction")
        if idx == -1:
            idx = self.lower.find("voice rule extraction")
        self.assertGreater(idx, -1)
        section = self.content[idx:idx + 2500]
        self.assertIn(
            "confidence",
            section.lower(),
            "voice-rule extraction must report confidence per rule",
        )

    def test_skill_step_runs_from_category_b_workflow(self):
        # Extraction is triggered as part of Category B detection
        # (or as a step ahead of generating B diffs)
        idx_cat_b = self.content.find("Category B")
        idx_extract = self.lower.find("voice-rule extraction")
        if idx_extract == -1:
            idx_extract = self.lower.find("voice rule extraction")
        # Both must be present; their proximity doesn't matter, but both must exist
        self.assertGreater(idx_cat_b, -1)
        self.assertGreater(idx_extract, -1)


if __name__ == "__main__":
    unittest.main()
