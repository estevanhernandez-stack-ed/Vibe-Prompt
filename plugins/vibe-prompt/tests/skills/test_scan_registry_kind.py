"""
Task 13 (v0.7) — TDD tests for registry-kind classification step in scan/SKILL.md.

Doc-based assertions following the project's testing convention.

Synthetic fixtures the SKILL.md must handle:
  - Fixture A: file with `export const PROMPTS = { foo: "string content...", ... }`
      → `registry.kind: "prompt-content"`
  - Fixture B: file with `export const MODELS = { mainChat: "gemini-2.5-pro", ... }`
      → `registry.kind: "model-routing"`
  - Fixture C: file with `export const TASKS = { generate: { description: ..., inputs: [...] } }`
      → `registry.kind: "task-mapping"`
  - Fixture D: file mixing string prompts AND model IDs
      → `registry.kind: "hybrid"`

The classification step must be declared in scan/SKILL.md and defer to
references/registry-kind-classification.md for the heuristic rules.
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
SCAN_SKILL = SKILLS_DIR / "scan" / "SKILL.md"
REGISTRY_KIND_REF = (
    SKILLS_DIR / "scan" / "references" / "registry-kind-classification.md"
)


class TestScanRegistryKindClassification(unittest.TestCase):
    def setUp(self):
        self.skill = SCAN_SKILL.read_text(encoding="utf-8")
        self.ref = REGISTRY_KIND_REF.read_text(encoding="utf-8")
        self.combined = self.skill + "\n" + self.ref

    def test_skill_declares_registry_kind_classification_step(self):
        """SKILL.md must declare a registry-kind classification step."""
        self.assertIn(
            "registry-kind-classification.md",
            self.skill,
            "scan/SKILL.md must link to references/registry-kind-classification.md",
        )

    def test_skill_emits_registry_kind_field(self):
        """SKILL.md must emit registry.kind on the inventory output."""
        self.assertIn(
            "registry.kind",
            self.skill,
            "scan/SKILL.md must declare emission of registry.kind",
        )

    def test_fixture_a_prompt_content(self):
        """Fixture A (PROMPTS string-valued) classifies prompt-content."""
        self.assertIn(
            "prompt-content",
            self.combined,
            "must document prompt-content classification for string-valued registries",
        )

    def test_fixture_b_model_routing(self):
        """Fixture B (MODELS task-id -> model-id) classifies model-routing."""
        self.assertIn(
            "model-routing",
            self.combined,
            "must document model-routing classification for model-id-valued registries",
        )

    def test_fixture_c_task_mapping(self):
        """Fixture C (TASKS object-valued descriptors) classifies task-mapping."""
        self.assertIn(
            "task-mapping",
            self.combined,
            "must document task-mapping classification for object-descriptor registries",
        )

    def test_fixture_d_hybrid(self):
        """Fixture D (mixed strings + model IDs) classifies hybrid."""
        self.assertIn(
            "hybrid",
            self.combined,
            "must document hybrid classification for mixed-shape registries",
        )

    def test_classification_step_runs_after_registry_detection(self):
        """Classification must run after step 3 (Registry detection)."""
        skill_lower = self.skill.lower()
        registry_detection_idx = skill_lower.find("registry detection")
        registry_kind_idx = skill_lower.find("registry-kind")
        # Both must exist
        self.assertGreaterEqual(
            registry_detection_idx,
            0,
            "Registry detection step must exist",
        )
        self.assertGreaterEqual(
            registry_kind_idx,
            0,
            "Registry-kind classification step must exist in SKILL.md",
        )
        # Classification runs after detection
        self.assertLess(
            registry_detection_idx,
            registry_kind_idx,
            "registry-kind classification must run after registry detection",
        )


if __name__ == "__main__":
    unittest.main()
