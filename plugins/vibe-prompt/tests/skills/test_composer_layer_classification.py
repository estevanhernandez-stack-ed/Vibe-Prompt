r"""
Task 13 — TDD tests for composer layer tracing + classification.

Asserts (per spec §4 step 3):
  1. composer-detection.md declares Stage 2 (tracing) and Stage 3 (classification)
  2. Layer types enumerated: global-directive, format-directive, knowledge-context, task-instruction, user-data
  3. Heuristics documented:
     - persona/directive content → global-directive
     - format/style/output content → format-directive
     - knowledge/lore/context with system origin → knowledge-context
     - systemInstruction/taskPrompt param → task-instruction
     - user-controlled var interpolation → user-data
  4. Layer-tracing covers += accumulation, template-literal, array-join patterns
  5. Per-layer confidence band declared (0.95 / 0.80 / 0.65 / 0.40)
  6. Layer order preserved from source appearance
  7. Mapping to composer.schema.json type enum documented (semantic → type)
  8. Concrete Celestia3 walkthrough included as worked example
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
COMPOSER_DETECTION_REF = SKILLS_DIR / "first-run-setup" / "references" / "composer-detection.md"


class TestComposerLayerClassification(unittest.TestCase):

    def setUp(self):
        self.ref = COMPOSER_DETECTION_REF.read_text(encoding="utf-8")

    def test_stage_2_tracing_documented(self):
        ref_lower = self.ref.lower()
        self.assertTrue(
            "stage 2" in ref_lower and ("tracing" in ref_lower or "layer trac" in ref_lower),
            "composer-detection.md must declare Stage 2 (layer tracing)",
        )

    def test_stage_3_classification_documented(self):
        ref_lower = self.ref.lower()
        self.assertTrue(
            "stage 3" in ref_lower and "classif" in ref_lower,
            "composer-detection.md must declare Stage 3 (layer classification)",
        )

    def test_all_five_layer_types_enumerated(self):
        for layer_type in [
            "global-directive",
            "format-directive",
            "knowledge-context",
            "task-instruction",
            "user-data",
        ]:
            self.assertIn(
                layer_type,
                self.ref,
                f"composer-detection.md must enumerate layer type '{layer_type}'",
            )

    def test_persona_directive_heuristic(self):
        """persona/directive content → global-directive."""
        ref_lower = self.ref.lower()
        has = (
            "persona" in ref_lower
            and "directive" in ref_lower
            and "global-directive" in self.ref
        )
        self.assertTrue(
            has,
            "Heuristic: persona/directive content → global-directive must be documented",
        )

    def test_format_style_output_heuristic(self):
        """format/style/output content → format-directive."""
        ref_lower = self.ref.lower()
        has = (
            "format" in ref_lower
            and ("style" in ref_lower or "output" in ref_lower)
            and "format-directive" in self.ref
        )
        self.assertTrue(
            has,
            "Heuristic: format/style/output → format-directive must be documented",
        )

    def test_knowledge_context_heuristic(self):
        """knowledge/lore/context with system origin → knowledge-context."""
        ref_lower = self.ref.lower()
        has = (
            "knowledge" in ref_lower
            and ("lore" in ref_lower or "context" in ref_lower)
            and "knowledge-context" in self.ref
        )
        self.assertTrue(
            has,
            "Heuristic: knowledge/lore/context → knowledge-context must be documented",
        )

    def test_task_instruction_heuristic(self):
        """systemInstruction / taskPrompt param → task-instruction."""
        has = (
            "systemInstruction" in self.ref
            and "task-instruction" in self.ref
        )
        self.assertTrue(
            has,
            "Heuristic: systemInstruction/taskPrompt → task-instruction must be documented",
        )

    def test_user_data_heuristic(self):
        """user-controlled var interpolation → user-data."""
        ref_lower = self.ref.lower()
        has = (
            "user-controlled" in self.ref
            and "user-data" in self.ref
        )
        self.assertTrue(
            has,
            "Heuristic: user-controlled var → user-data must be documented",
        )

    def test_concatenation_patterns_documented(self):
        """Tracing covers += accumulation, template-literal, array-join."""
        has_accum = "+=" in self.ref
        has_template_literal = "template literal" in self.ref.lower() or "template-literal" in self.ref.lower()
        has_array_join = "join" in self.ref.lower() and "array" in self.ref.lower()
        self.assertTrue(
            has_accum and has_template_literal and has_array_join,
            "composer-detection.md must document all three concat patterns (+= accumulation, template-literal, array.join)",
        )

    def test_per_layer_confidence_band(self):
        """Confidence band: 0.95 / 0.80 / 0.65 / 0.40."""
        for c in ["0.95", "0.80", "0.65", "0.40"]:
            self.assertIn(
                c,
                self.ref,
                f"Per-layer confidence band must include {c}",
            )

    def test_layer_order_preserved(self):
        ref_lower = self.ref.lower()
        has_order = (
            "order" in ref_lower
            and ("source-file" in ref_lower or "source file" in ref_lower or "top-to-bottom" in ref_lower or "appearance" in ref_lower)
        )
        self.assertTrue(
            has_order,
            "Layer order preserved from source-file appearance must be documented",
        )

    def test_schema_type_mapping_documented(self):
        """Spec semantic layers → composer.schema.json type enum mapping."""
        # composer schema type enum: literal | directive-field | knowledge-injection | task-instruction | conditional
        ref = self.ref
        has_mapping = (
            "directive-field" in ref
            and "knowledge-injection" in ref
            and "task-instruction" in ref
        )
        self.assertTrue(
            has_mapping,
            "Mapping semantic layer → composer.schema.json type enum must be documented",
        )

    def test_celestia3_walkthrough_present(self):
        """Concrete worked example (Celestia3 gemini.ts) included."""
        ref_lower = self.ref.lower()
        has_walkthrough = "celestia3" in ref_lower or "technomancer" in ref_lower
        self.assertTrue(
            has_walkthrough,
            "Concrete Celestia3 walkthrough must be included",
        )


if __name__ == "__main__":
    unittest.main()
