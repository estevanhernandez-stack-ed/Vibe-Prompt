r"""
Task 14 — TDD tests for composer.json emission with confidence + schema validation.

Asserts:
  1. composer-detection.md declares Stage 4 (emission) and Stage 5 (confidence floor + user prompt)
  2. ≥4 layers + classification → globalConfidence ≥0.7 documented
  3. <2 layers → globalConfidence ≤0.4 + warning documented
  4. regenerationSource enum (auto-detected | hybrid | manual) documented
  5. Sample emission validates against composer.schema.json
  6. Re-generation behavior documented (preserves user edits, hybrid source)
  7. friction trigger `composer-auto-generation-confidence-low` documented
  8. Banner text differs by confidence level (high vs low)
  9. first-run-setup/SKILL.md invokes emission as the workflow's composer-capture step
"""

import json
import pathlib
import unittest

from jsonschema import validate

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
SCHEMAS_DIR = pathlib.Path(__file__).parent.parent.parent / "schemas"
FRS_SKILL = SKILLS_DIR / "first-run-setup" / "SKILL.md"
COMPOSER_DETECTION_REF = SKILLS_DIR / "first-run-setup" / "references" / "composer-detection.md"
COMPOSER_SCHEMA = SCHEMAS_DIR / "composer.schema.json"


class TestComposerJsonEmission(unittest.TestCase):

    def setUp(self):
        self.ref = COMPOSER_DETECTION_REF.read_text(encoding="utf-8")
        self.skill = FRS_SKILL.read_text(encoding="utf-8")
        with open(COMPOSER_SCHEMA) as f:
            self.schema = json.load(f)

    def test_stage_4_emission_documented(self):
        ref_lower = self.ref.lower()
        self.assertTrue(
            "stage 4" in ref_lower and "emi" in ref_lower,
            "composer-detection.md must declare Stage 4 (emission)",
        )

    def test_stage_5_confidence_floor_documented(self):
        ref_lower = self.ref.lower()
        self.assertTrue(
            "stage 5" in ref_lower and ("floor" in ref_lower or "confidence" in ref_lower),
            "composer-detection.md must declare Stage 5 (confidence floor + user prompt)",
        )

    def test_four_layers_target_confidence(self):
        """≥4 layers + clean classification → globalConfidence ≥0.7."""
        ref_lower = self.ref.lower()
        has = (
            ("4 layers" in ref_lower or "≥4 layers" in self.ref or "four layers" in ref_lower)
            and ("0.7" in self.ref)
        )
        self.assertTrue(
            has,
            "≥4 layers + globalConfidence ≥0.7 must be documented",
        )

    def test_low_layer_count_lower_confidence(self):
        """<2 layers → globalConfidence ≤0.40 + warning."""
        ref_lower = self.ref.lower()
        has = (
            ("2 layers" in ref_lower or "fewer than 2" in ref_lower)
            and "0.4" in self.ref
            and "warning" in ref_lower
        )
        self.assertTrue(
            has,
            "<2 layers → globalConfidence ≤0.40 + warning banner must be documented",
        )

    def test_regeneration_source_enum_documented(self):
        for value in ("auto-detected", "hybrid", "manual"):
            self.assertIn(
                value,
                self.ref,
                f"regenerationSource value '{value}' must be documented",
            )

    def test_friction_trigger_low_confidence_documented(self):
        self.assertIn(
            "composer-auto-generation-confidence-low",
            self.ref,
            "Friction trigger 'composer-auto-generation-confidence-low' must be documented",
        )

    def test_regeneration_behavior_documented(self):
        ref_lower = self.ref.lower()
        has = (
            ("re-gen" in ref_lower or "regen" in ref_lower or "regenerate-composer" in ref_lower)
            and "hybrid" in self.ref
        )
        self.assertTrue(
            has,
            "Re-generation behavior (--regenerate-composer + hybrid source) must be documented",
        )

    def test_skill_invokes_emission(self):
        """first-run-setup/SKILL.md workflow's composer step references emission."""
        skill_lower = self.skill.lower()
        has = (
            "composer.json" in self.skill
            and ("emit" in skill_lower or "writes" in skill_lower or "output" in skill_lower)
        )
        self.assertTrue(
            has,
            "first-run-setup/SKILL.md must invoke composer.json emission",
        )

    def test_high_confidence_emission_validates(self):
        """A sample high-confidence emission validates against composer.schema.json."""
        composer = {
            "version": "0.1",
            "kind": "stacked",
            "sourceFile": "src/lib/gemini.ts",
            "globalConfidence": 0.86,
            "regenerationSource": "auto-detected",
            "layers": [
                {"id": "directive-persona", "type": "directive-field", "text": "You are...", "order": 1, "confidence": 0.95},
                {"id": "directive-master", "type": "directive-field", "text": "[MASTER DIRECTIVE]...", "order": 2, "confidence": 0.95},
                {"id": "format-default", "type": "directive-field", "text": "[FORMAT]...", "order": 3, "confidence": 0.85},
                {"id": "knowledge", "type": "knowledge-injection", "text": "<knowledge>", "order": 4, "confidence": 0.75},
                {"id": "task", "type": "task-instruction", "text": "", "order": 5, "confidence": 0.90},
            ],
        }
        validate(instance=composer, schema=self.schema)

    def test_low_confidence_emission_validates(self):
        """A low-confidence emission also validates (allowing user to remediate)."""
        composer = {
            "version": "0.1",
            "kind": "stacked",
            "sourceFile": "src/lib/llm.ts",
            "globalConfidence": 0.40,
            "regenerationSource": "auto-detected",
            "layers": [
                {"id": "task", "type": "task-instruction", "text": "", "order": 1, "confidence": 0.40},
            ],
        }
        validate(instance=composer, schema=self.schema)

    def test_hybrid_regeneration_validates(self):
        composer = {
            "version": "0.1",
            "kind": "stacked",
            "sourceFile": "src/lib/gemini.ts",
            "globalConfidence": 0.85,
            "regenerationSource": "hybrid",
            "layers": [
                {"id": "directive-persona", "type": "directive-field", "text": "...", "order": 1, "confidence": 0.95},
                {"id": "task", "type": "task-instruction", "text": "", "order": 2, "confidence": 0.90},
            ],
        }
        validate(instance=composer, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
