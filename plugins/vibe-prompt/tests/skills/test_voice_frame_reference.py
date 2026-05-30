"""
Task 14 — TDD tests for skills/remediate/references/voice-frame-detection.md.

Asserts the new v0.6 reference file exists and declares all three required
sections per spec §5 (Category B voice-frame depth) plus the regex pattern table
for archaic vocabulary, ritualistic framing, and capitalized abstract nouns.
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
VOICE_FRAME_DETECTION = (
    SKILLS_DIR / "remediate" / "references" / "voice-frame-detection.md"
)


class TestVoiceFrameDetectionReference(unittest.TestCase):

    def setUp(self):
        self.assertTrue(
            VOICE_FRAME_DETECTION.exists(),
            f"references/voice-frame-detection.md must exist at {VOICE_FRAME_DETECTION}",
        )
        self.content = VOICE_FRAME_DETECTION.read_text(encoding="utf-8")
        self.lower = self.content.lower()

    def test_has_voice_rule_extraction_section(self):
        self.assertIn(
            "Voice-rule extraction from global directive",
            self.content,
            "reference must declare 'Voice-rule extraction from global directive' section",
        )

    def test_has_voice_frame_phrase_patterns_section(self):
        self.assertIn(
            "Voice-frame phrase patterns",
            self.content,
            "reference must declare 'Voice-frame phrase patterns' section",
        )

    def test_has_confidence_calibration_section(self):
        self.assertIn(
            "Confidence calibration",
            self.content,
            "reference must declare 'Confidence calibration' section",
        )

    def test_archaic_vocabulary_regex_documented(self):
        # Must include archaic patterns from spec §5
        for token in ["thou", "verily", "ancient", "veil", "quatrain"]:
            self.assertIn(
                token,
                self.lower,
                f"archaic-vocabulary pattern must include `{token}`",
            )

    def test_ritualistic_framing_patterns_documented(self):
        # Must capture the cosmos / divine / source patterns from spec §5
        self.assertIn(
            "ritualistic",
            self.lower,
            "reference must document ritualistic framing pattern",
        )
        ritualistic_anchors = ["the cosmos", "the divine", "the source"]
        hits = sum(1 for anchor in ritualistic_anchors if anchor in self.lower)
        self.assertGreaterEqual(
            hits, 2,
            "ritualistic-framing pattern table must reference at least 2 archetypes",
        )

    def test_capitalized_abstract_nouns_documented(self):
        self.assertIn(
            "capitalized abstract",
            self.lower,
            "reference must document capitalized abstract noun pattern",
        )
        # Pilgrim and Way are the spec examples
        self.assertIn("Pilgrim", self.content)
        self.assertIn("Way", self.content)

    def test_includes_regex_pattern_table(self):
        # Table format: at least one markdown table header pipe row
        self.assertIn("|", self.content, "voice-frame patterns require a markdown table")
        self.assertIn("regex", self.lower, "pattern table must reference regex column")

    def test_confidence_drops_to_0_65_for_voice_frame(self):
        # Spec §5: voice-frame extension drops to 0.65
        self.assertIn(
            "0.65",
            self.content,
            "Confidence calibration must declare 0.65 for voice-frame rewrite",
        )

    def test_banned_phrase_confidence_0_75_documented(self):
        # The split: banned-phrase removal stays at 0.75
        self.assertIn(
            "0.75",
            self.content,
            "Confidence calibration must contrast with 0.75 banned-phrase confidence",
        )


if __name__ == "__main__":
    unittest.main()
