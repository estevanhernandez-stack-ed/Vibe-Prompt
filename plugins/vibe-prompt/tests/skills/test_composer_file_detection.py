r"""
Task 12 — TDD tests for composer file detection in first-run-setup/SKILL.md.

Heuristics per spec §4 step 1:
- Filename matches: gemini.ts, openai.ts, anthropic.ts, llm.ts, ai.ts, chat.ts
- SDK imports: @google/genai, @anthropic-ai/sdk, openai

Asserts:
  1. first-run-setup/references/composer-detection.md exists
  2. Filename heuristic documented (lists known composer filenames)
  3. SDK import heuristic documented (@google/genai, @anthropic-ai/sdk, openai)
  4. Detection emits candidates with reason strings
  5. Multi-candidate output supported (a repo may have multiple composer files)
  6. first-run-setup/SKILL.md references composer-detection.md
  7. Workflow invokes detection during setup
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
FRS_SKILL = SKILLS_DIR / "first-run-setup" / "SKILL.md"
COMPOSER_DETECTION_REF = SKILLS_DIR / "first-run-setup" / "references" / "composer-detection.md"


class TestComposerFileDetectionDocumentation(unittest.TestCase):

    def setUp(self):
        self.skill = FRS_SKILL.read_text(encoding="utf-8")
        self.ref = (
            COMPOSER_DETECTION_REF.read_text(encoding="utf-8")
            if COMPOSER_DETECTION_REF.exists()
            else ""
        )

    def test_composer_detection_reference_exists(self):
        self.assertTrue(
            COMPOSER_DETECTION_REF.exists(),
            "first-run-setup/references/composer-detection.md must exist",
        )

    def test_filename_heuristic_documented(self):
        """Lists filenames: gemini.ts, openai.ts, anthropic.ts, llm.ts, ai.ts, chat.ts."""
        required_filenames = ["gemini.ts", "openai.ts", "anthropic.ts", "llm.ts", "ai.ts", "chat.ts"]
        missing = [fn for fn in required_filenames if fn not in self.ref]
        self.assertEqual(
            missing,
            [],
            f"composer-detection.md must list filename candidates: missing {missing}",
        )

    def test_sdk_import_heuristic_documented(self):
        """SDK imports declared: @google/genai, @anthropic-ai/sdk, openai."""
        required_imports = ["@google/genai", "@anthropic-ai/sdk", "openai"]
        missing = [imp for imp in required_imports if imp not in self.ref]
        self.assertEqual(
            missing,
            [],
            f"composer-detection.md must list SDK imports: missing {missing}",
        )

    def test_emits_candidates_with_reason(self):
        """Detection output must include candidates + reason strings."""
        ref_lower = self.ref.lower()
        has_reason = (
            "reason" in ref_lower
            and "candidate" in ref_lower
        )
        self.assertTrue(
            has_reason,
            "composer-detection.md must emit candidates with reason strings",
        )

    def test_multi_candidate_supported(self):
        """Multi-composer-file repos supported (each detected as a candidate)."""
        ref_lower = self.ref.lower()
        has_multi = (
            "multiple" in ref_lower
            or "multi" in ref_lower
            or "each" in ref_lower
        )
        self.assertTrue(
            has_multi,
            "composer-detection.md must support multi-candidate output",
        )

    def test_skill_references_composer_detection(self):
        self.assertIn(
            "composer-detection",
            self.skill,
            "first-run-setup/SKILL.md must reference composer-detection.md",
        )

    def test_workflow_invokes_detection(self):
        """Setup workflow must invoke composer-file detection."""
        skill_lower = self.skill.lower()
        has_invoke = (
            "detect" in skill_lower
            and "composer" in skill_lower
        )
        self.assertTrue(
            has_invoke,
            "first-run-setup/SKILL.md workflow must invoke composer file detection",
        )


if __name__ == "__main__":
    unittest.main()
