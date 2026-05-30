"""
Task 8 — TDD tests for composer.json emission with apiParameter populated.

v0.6 emits apiParameter + apiParameterConfidence on every layer. globalConfidence
reflects the apiParameter signal (it's part of the weighted average). Backward
compat: v0.5 composer.json without apiParameter still validates (optional field
at schema level).

Asserts:
  1. SKILL Stage 4 emission step includes apiParameter in layer output shape
  2. SKILL emission step includes apiParameterConfidence in layer output shape
  3. globalConfidence formula references apiParameter confidence signal
  4. Backward compat: schema allows missing apiParameter (validated against schema)
"""

import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent.parent.parent
SKILLS_DIR = ROOT / "skills"
FIRST_RUN_SKILL = SKILLS_DIR / "first-run-setup" / "SKILL.md"
COMPOSER_DETECTION = SKILLS_DIR / "first-run-setup" / "references" / "composer-detection.md"
COMPOSER_SCHEMA = ROOT / "schemas" / "composer.schema.json"


class TestComposerEmissionV06(unittest.TestCase):

    def setUp(self):
        self.skill = FIRST_RUN_SKILL.read_text(encoding="utf-8")
        self.detection = COMPOSER_DETECTION.read_text(encoding="utf-8")
        self.schema = json.loads(COMPOSER_SCHEMA.read_text(encoding="utf-8"))

    def test_emission_step_includes_apiparameter(self):
        """SKILL Stage 2b or Stage 4 must declare apiParameter on emitted layers."""
        has_emit = "apiParameter" in self.skill
        self.assertTrue(
            has_emit,
            "first-run-setup/SKILL.md must declare apiParameter in emission step"
        )

    def test_emission_step_includes_apiparameter_confidence(self):
        has_emit_conf = "apiParameterConfidence" in self.skill or "apiParameterConfidence" in self.detection
        self.assertTrue(
            has_emit_conf,
            "first-run-setup must emit apiParameterConfidence per layer"
        )

    def test_global_confidence_reflects_apiparameter_signal(self):
        """globalConfidence formula in Stage 4 should reference apiParameter signal."""
        # Check that detection or skill mentions weighting apiParameter into globalConfidence
        combined = self.skill + self.detection
        has_weight = (
            "weighted" in combined.lower()
            and "apiParameter" in combined
        )
        self.assertTrue(
            has_weight,
            "globalConfidence weighting must include apiParameter signal"
        )

    def test_backward_compat_apiparameter_optional_in_schema(self):
        """v0.5 composer.json (no apiParameter) must validate against v0.6 schema."""
        # Schema's required list on layer must NOT include apiParameter
        items = self.schema["properties"]["layers"]["items"]
        required = items.get("required", [])
        self.assertNotIn(
            "apiParameter",
            required,
            "composer.schema.json layer required must NOT include apiParameter (backward compat)"
        )

    def test_backward_compat_v05_sample_validates(self):
        """A v0.5-style composer.json (no apiParameter field) must validate."""
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not installed")

        v05_sample = {
            "version": "0.1",
            "kind": "stacked",
            "sourceFile": "src/lib/gemini.ts",
            "globalConfidence": 0.85,
            "regenerationSource": "auto-detected",
            "layers": [
                {
                    "id": "directive-persona",
                    "type": "directive-field",
                    "text": "You are ...",
                    "order": 1,
                    "confidence": 0.95
                }
            ]
        }
        # Should not raise
        jsonschema.validate(v05_sample, self.schema)

    def test_v06_sample_with_apiparameter_validates(self):
        """v0.6 composer.json with apiParameter populated must validate."""
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not installed")

        v06_sample = {
            "version": "0.1",
            "kind": "stacked",
            "sourceFile": "src/lib/gemini.ts",
            "globalConfidence": 0.88,
            "regenerationSource": "auto-detected",
            "layers": [
                {
                    "id": "directive-persona",
                    "type": "global-directive",
                    "text": "You are ...",
                    "order": 1,
                    "confidence": 0.95,
                    "apiParameter": "systemInstruction",
                    "apiParameterConfidence": 0.95
                },
                {
                    "id": "task-user-data",
                    "type": "task-instruction",
                    "text": "",
                    "order": 5,
                    "confidence": 0.90,
                    "apiParameter": "contents",
                    "apiParameterConfidence": 0.85
                }
            ]
        }
        jsonschema.validate(v06_sample, self.schema)


if __name__ == "__main__":
    unittest.main()
