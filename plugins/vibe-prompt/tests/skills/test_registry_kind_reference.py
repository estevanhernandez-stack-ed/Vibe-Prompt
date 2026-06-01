"""
Task 9 (v0.7) — TDD tests for registry-kind-classification.md reference.

Asserts:
  1. File exists at skills/scan/references/registry-kind-classification.md
  2. Sections present for each kind:
     - "prompt-content registry"
     - "model-routing registry"
     - "task-mapping registry"
     - "hybrid registry"
  3. Each section includes detection heuristics + canonical fixture example
  4. model-routing section references the 626Labs `config/modelRegistry.ts`
     pattern (task-id -> model-id mapping)
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
REGISTRY_KIND_REF = (
    SKILLS_DIR / "scan" / "references" / "registry-kind-classification.md"
)


class TestRegistryKindReference(unittest.TestCase):
    def setUp(self):
        self.path = REGISTRY_KIND_REF

    def test_file_exists(self):
        self.assertTrue(
            self.path.exists(),
            f"registry-kind-classification.md must exist at {self.path}",
        )

    def test_contains_prompt_content_section(self):
        content = self.path.read_text(encoding="utf-8")
        self.assertIn(
            "prompt-content registry",
            content,
            "must contain 'prompt-content registry' section",
        )

    def test_contains_model_routing_section(self):
        content = self.path.read_text(encoding="utf-8")
        self.assertIn(
            "model-routing registry",
            content,
            "must contain 'model-routing registry' section",
        )

    def test_contains_task_mapping_section(self):
        content = self.path.read_text(encoding="utf-8")
        self.assertIn(
            "task-mapping registry",
            content,
            "must contain 'task-mapping registry' section",
        )

    def test_contains_hybrid_section(self):
        content = self.path.read_text(encoding="utf-8")
        self.assertIn(
            "hybrid registry",
            content,
            "must contain 'hybrid registry' section",
        )

    def test_each_section_has_detection_heuristic(self):
        content = self.path.read_text(encoding="utf-8").lower()
        # Each section should describe detection signals (regex / pattern /
        # heuristic / signal language)
        self.assertIn("heuristic", content, "must document detection heuristics")

    def test_each_section_has_canonical_example(self):
        content = self.path.read_text(encoding="utf-8").lower()
        self.assertIn(
            "example",
            content,
            "must include canonical fixture examples",
        )

    def test_model_routing_references_626labs_pattern(self):
        content = self.path.read_text(encoding="utf-8")
        self.assertIn(
            "config/modelRegistry.ts",
            content,
            "model-routing section must reference 626Labs config/modelRegistry.ts",
        )

    def test_model_routing_mentions_task_id_to_model_id(self):
        content = self.path.read_text(encoding="utf-8").lower()
        # task-id -> model-id mapping language
        has_mapping = (
            "task-id" in content and "model-id" in content
        ) or "task -> model" in content or "task → model" in content
        self.assertTrue(
            has_mapping,
            "model-routing section must describe task-id -> model-id mapping",
        )


if __name__ == "__main__":
    unittest.main()
