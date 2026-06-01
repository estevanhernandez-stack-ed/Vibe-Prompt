"""
Task 14 — TDD tests for composer-kinds.md reference (v0.7).

v0.7 introduces four composer topology kinds: single-composer, multi-composer,
multi-call-site, shared-package. Each kind has detection heuristics + a
canonical example from the cross-app probe (Celestia3, 626Labs, WeSeeYou,
Quiz Show). Multi-call-site groups by SDK + persona.

Asserts:
  1. File exists at expected location
  2. Sections for each of the 4 kinds present
  3. Each section has detection heuristic + canonical example
  4. single-composer references Celestia3 src/lib/gemini.ts
  5. multi-composer references 626Labs galaxyCore.ts + ChatController.ts
  6. multi-call-site references WeSeeYou (no canonical file; 6 inline call sites)
  7. shared-package references Quiz Show packages/ai/src/gemini/GeminiService.ts
  8. Multi-call-site grouping heuristic subsection: same-SDK + same-persona groups
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
COMPOSER_KINDS = SKILLS_DIR / "first-run-setup" / "references" / "composer-kinds.md"


class TestComposerKindsReference(unittest.TestCase):

    def setUp(self):
        self.assertTrue(
            COMPOSER_KINDS.exists(),
            f"composer-kinds.md must exist at {COMPOSER_KINDS}"
        )
        self.text = COMPOSER_KINDS.read_text(encoding="utf-8")

    def test_file_exists(self):
        self.assertTrue(COMPOSER_KINDS.exists())

    def test_single_composer_section(self):
        self.assertIn(
            "single-composer",
            self.text,
            "composer-kinds.md must have a single-composer section"
        )

    def test_multi_composer_section(self):
        self.assertIn(
            "multi-composer",
            self.text,
            "composer-kinds.md must have a multi-composer section"
        )

    def test_multi_call_site_section(self):
        self.assertIn(
            "multi-call-site",
            self.text,
            "composer-kinds.md must have a multi-call-site section"
        )

    def test_shared_package_section(self):
        self.assertIn(
            "shared-package",
            self.text,
            "composer-kinds.md must have a shared-package section"
        )

    def test_single_composer_celestia3_example(self):
        self.assertTrue(
            "Celestia3" in self.text and "gemini.ts" in self.text,
            "single-composer must reference Celestia3 src/lib/gemini.ts"
        )

    def test_multi_composer_626labs_example(self):
        has_galaxy = "galaxyCore" in self.text
        has_chat_ctrl = "ChatController" in self.text
        self.assertTrue(
            has_galaxy and has_chat_ctrl,
            "multi-composer must reference 626Labs galaxyCore + ChatController"
        )

    def test_multi_call_site_weseeyou_example(self):
        has_weseeyou = "WeSeeYou" in self.text
        has_inline = "inline" in self.text.lower() or "call site" in self.text.lower()
        self.assertTrue(
            has_weseeyou and has_inline,
            "multi-call-site must reference WeSeeYou with no canonical file / 6 inline call sites"
        )

    def test_shared_package_quizshow_example(self):
        has_quiz = "Quiz Show" in self.text or "QuizShow" in self.text
        has_pkg = "packages/ai" in self.text or "GeminiService" in self.text
        self.assertTrue(
            has_quiz and has_pkg,
            "shared-package must reference Quiz Show packages/ai/src/gemini/GeminiService.ts"
        )

    def test_multi_call_site_grouping_heuristic(self):
        """Same-SDK + same-persona groups; differing personas don't."""
        has_grouping = "grouping" in self.text.lower() or "group" in self.text.lower()
        has_persona = "persona" in self.text.lower()
        has_sdk = "SDK" in self.text or "sdk" in self.text
        self.assertTrue(
            has_grouping and has_persona and has_sdk,
            "composer-kinds.md must document multi-call-site grouping by SDK + persona"
        )

    def test_detection_heuristics_per_kind(self):
        """Each kind section should include detection heuristics."""
        has_heuristic = "heuristic" in self.text.lower() or "detection" in self.text.lower()
        self.assertTrue(
            has_heuristic,
            "composer-kinds.md must document detection heuristics per kind"
        )


if __name__ == "__main__":
    unittest.main()
