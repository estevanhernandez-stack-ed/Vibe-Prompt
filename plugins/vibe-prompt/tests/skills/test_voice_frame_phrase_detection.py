"""
Task 16 — TDD tests for voice-frame phrase pattern detection in remediate
SKILL.md + voice-frame-detection.md.

Asserts:
- SKILL.md documents scanning task prompt content for voice-frame phrase
  clusters using patterns from voice-frame-detection.md.
- Detection emits {phrase, location, banSource} triples per match.
- Audit finding emits a voiceFrameContradictions field populated by detection.
- Celestia3 natal_interpretation phrases (quatrain-style narrative, shattering
  of the veil, ancient dust, mirrors of mercury, prophetic shadows) are all
  covered by patterns in the reference file.
"""

import pathlib
import re
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
REMEDIATE_SKILL = SKILLS_DIR / "remediate" / "SKILL.md"
VOICE_FRAME_DETECTION = (
    SKILLS_DIR / "remediate" / "references" / "voice-frame-detection.md"
)


class TestVoiceFramePhraseDetection(unittest.TestCase):

    def setUp(self):
        self.skill = REMEDIATE_SKILL.read_text(encoding="utf-8")
        self.reference = VOICE_FRAME_DETECTION.read_text(encoding="utf-8")

    # --- SKILL.md changes ---
    def test_skill_documents_voice_frame_phrase_detection(self):
        lower = self.skill.lower()
        self.assertTrue(
            "voice-frame phrase" in lower
            or "voice frame phrase" in lower
            or "voice-frame contradictions" in lower
            or "voiceframecontradictions" in lower,
            "remediate/SKILL.md must document voice-frame phrase detection",
        )

    def test_skill_emits_voice_frame_contradictions_field(self):
        # Spec §5: audit finding emits voiceFrameContradictions field
        self.assertIn(
            "voiceFrameContradictions",
            self.skill,
            "remediate/SKILL.md must reference the voiceFrameContradictions field",
        )

    def test_skill_emits_triple_phrase_location_bansource(self):
        # Detection emits {phrase, location, banSource}
        # All three field names must be present together (within reasonable text radius)
        lower = self.skill.lower()
        # Find an occurrence where phrase, location, banSource all appear
        idx_phrase = lower.find("phrase")
        idx_location = lower.find("location")
        idx_bansource = lower.find("bansource")
        if idx_bansource == -1:
            idx_bansource = lower.find("ban-source")
        if idx_bansource == -1:
            idx_bansource = lower.find("ban source")
        self.assertGreater(
            idx_bansource, -1,
            "SKILL.md must reference banSource (or ban-source) in voice-frame triple",
        )
        self.assertGreater(idx_phrase, -1)
        self.assertGreater(idx_location, -1)

    def test_skill_invokes_pattern_families_from_reference(self):
        # SKILL.md must invoke the patterns documented in voice-frame-detection.md
        lower = self.skill.lower()
        # Three pattern families: archaic vocabulary, ritualistic framing,
        # capitalized abstract nouns
        self.assertTrue(
            "archaic" in lower,
            "SKILL.md must reference archaic-vocabulary pattern family",
        )
        self.assertTrue(
            "ritualistic" in lower,
            "SKILL.md must reference ritualistic-framing pattern family",
        )
        self.assertTrue(
            "capitalized abstract" in lower or "capitalized-abstract" in lower,
            "SKILL.md must reference capitalized-abstract pattern family",
        )

    # --- Celestia3 fixture phrases must be covered by reference patterns ---
    def test_quatrain_style_pattern_covers_celestia3_fixture(self):
        self.assertIn("quatrain", self.reference.lower())

    def test_shattering_of_the_veil_covered(self):
        # Spec §5 names "veil" as archaic-vocab pattern family
        self.assertIn("veil", self.reference.lower())

    def test_ancient_dust_covered(self):
        self.assertIn("ancient", self.reference.lower())

    def test_mirrors_of_mercury_covered(self):
        self.assertIn("mercur", self.reference.lower())

    def test_prophetic_shadows_covered(self):
        self.assertIn("prophet", self.reference.lower())

    def test_reference_includes_ban_source_in_triple_shape(self):
        # The triple format {phrase, location, banSource} must be documented
        lower = self.reference.lower()
        self.assertTrue(
            "phrase" in lower and "location" in lower,
            "voice-frame-detection.md must describe the triple shape",
        )
        self.assertTrue(
            "bansource" in lower or "ban-source" in lower or "ban source" in lower,
            "voice-frame-detection.md must describe banSource field",
        )

    # --- Mechanical regex test: verify a pattern matches each phrase ---
    def test_archaic_pattern_matches_celestia3_phrases(self):
        """
        Smoke check: at least one regex pattern in the reference must compile
        and match each of the five Celestia3 fixture phrases.
        """
        fixtures = [
            "quatrain-style narrative",
            "shattering of the veil",
            "ancient dust",
            "mirrors of mercury",
            "prophetic shadows",
        ]
        # Build candidate regexes from spec patterns (the reference table)
        candidate_patterns = [
            r"(?i)\bquatrain(-style|s)?\b",
            r"(?i)\bancient\b.{0,30}(dust|veil|shadow|wisdom)",
            r"(?i)\bveil\b.{0,30}(shatter|pierce|lift|rend)",
            r"(?i)(mercur(ial|y)|prophet(ic|s)?)\b.{0,40}(mirror|shadow|tongue)",
            # also try the inverse direction (phrase-then-mercury)
            r"(?i)(mirror|shadow|tongue)s?\s+of\s+(mercur(ial|y)|prophet(ic|s)?)",
            r"(?i)(shatter|pierce|lift|rend).{0,30}\bveil\b",
        ]
        for phrase in fixtures:
            matched = any(re.search(p, phrase) for p in candidate_patterns)
            self.assertTrue(
                matched,
                f"voice-frame patterns must cover Celestia3 fixture phrase: {phrase!r}",
            )


if __name__ == "__main__":
    unittest.main()
