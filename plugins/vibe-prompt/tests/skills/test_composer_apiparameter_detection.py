"""
Task 7 — TDD tests for apiParameter heuristics in composer detection.

v0.6 extends first-run-setup composer detection to identify which API parameter
each composer layer is destined for. This enables F12 API-parameter-aware
detection: when user-var layer is at `apiParameter: "contents"` and the
system-instruction layer is at `apiParameter: "systemInstruction"`, F12 does
NOT fire (structurally segregated).

Heuristics (per spec §1):
  - Layer concatenated into `systemInstruction:` arg → "systemInstruction"
  - Layer interpolated into `contents[].parts[].text` (Gemini) → "contents"
  - Layer interpolated into OpenAI `messages[].content` → "messages"
  - Layer interpolated into a single `prompt:` string (OpenAI completions) → "prompt"
  - Unknown call pattern → null (confidence 0.0)

Asserts:
  1. composer-detection.md declares the apiParameter heuristics catalog
  2. systemInstruction heuristic (Gemini systemInstruction: arg) documented
  3. contents heuristic (Gemini contents[].parts[].text) documented
  4. messages heuristic (OpenAI messages[].content) documented
  5. prompt heuristic (OpenAI completions prompt:) documented
  6. Unknown / null fallback documented (confidence 0.0)
  7. Confidence calibration documented (>=0.9 for systemInstruction, >=0.85 for contents)
  8. first-run-setup/SKILL.md invokes apiParameter detection during layer classification
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
FIRST_RUN_SKILL = SKILLS_DIR / "first-run-setup" / "SKILL.md"
COMPOSER_DETECTION = SKILLS_DIR / "first-run-setup" / "references" / "composer-detection.md"


class TestComposerApiParameterHeuristics(unittest.TestCase):

    def setUp(self):
        self.skill = FIRST_RUN_SKILL.read_text(encoding="utf-8")
        self.detection = COMPOSER_DETECTION.read_text(encoding="utf-8")

    def test_apiparameter_catalog_declared(self):
        self.assertIn(
            "apiParameter",
            self.detection,
            "composer-detection.md must declare apiParameter heuristics catalog"
        )

    def test_system_instruction_heuristic_documented(self):
        """Layer concatenated into systemInstruction: arg → apiParameter: systemInstruction."""
        has_si = (
            "systemInstruction" in self.detection
            and ("systemInstruction:" in self.detection
                 or "systemInstruction arg" in self.detection.lower()
                 or "systemInstruction parameter" in self.detection.lower())
        )
        self.assertTrue(
            has_si,
            "composer-detection.md must document systemInstruction: arg heuristic"
        )

    def test_contents_heuristic_documented(self):
        """Gemini contents[].parts[].text interpolation → apiParameter: contents."""
        has_contents = (
            "contents" in self.detection
            and ("parts[].text" in self.detection
                 or "parts" in self.detection.lower())
        )
        self.assertTrue(
            has_contents,
            "composer-detection.md must document Gemini contents[].parts[].text heuristic"
        )

    def test_messages_heuristic_documented(self):
        """OpenAI / Anthropic messages[].content → apiParameter: messages."""
        has_messages = (
            "messages" in self.detection
            and "content" in self.detection.lower()
        )
        self.assertTrue(
            has_messages,
            "composer-detection.md must document OpenAI/Anthropic messages[].content heuristic"
        )

    def test_prompt_heuristic_documented(self):
        """OpenAI completions prompt: string → apiParameter: prompt."""
        has_prompt = (
            "prompt" in self.detection.lower()
            and "completion" in self.detection.lower()
        )
        self.assertTrue(
            has_prompt,
            "composer-detection.md must document OpenAI completions prompt: heuristic"
        )

    def test_null_fallback_documented(self):
        """Unknown call pattern → null, confidence 0.0."""
        has_null = (
            "null" in self.detection.lower()
            and ("unknown" in self.detection.lower()
                 or "fallback" in self.detection.lower()
                 or "0.0" in self.detection)
        )
        self.assertTrue(
            has_null,
            "composer-detection.md must document null fallback with confidence 0.0"
        )

    def test_confidence_calibration_documented(self):
        """Confidence per heuristic: systemInstruction >=0.9, contents >=0.85."""
        has_conf = (
            "0.9" in self.detection
            and "0.85" in self.detection
        )
        self.assertTrue(
            has_conf,
            "composer-detection.md must document confidence calibration (0.9 / 0.85)"
        )

    def test_first_run_skill_invokes_apiparameter_detection(self):
        """first-run-setup/SKILL.md must invoke apiParameter detection in layer classification."""
        has_invoke = "apiParameter" in self.skill
        self.assertTrue(
            has_invoke,
            "first-run-setup/SKILL.md must invoke apiParameter detection during layer classification"
        )

    def test_apiparameter_enum_complete(self):
        """All 5 enum values present in catalog: systemInstruction, contents, messages, instructions, prompt."""
        for v in ["systemInstruction", "contents", "messages", "instructions", "prompt"]:
            self.assertIn(
                v,
                self.detection,
                f"composer-detection.md must reference enum value '{v}'"
            )


if __name__ == "__main__":
    unittest.main()
