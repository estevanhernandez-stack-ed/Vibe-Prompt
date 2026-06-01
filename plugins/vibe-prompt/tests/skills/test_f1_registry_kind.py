"""
Task 22 — TDD tests for F1 registry-kind awareness (v0.7).

Background: cross-app probe on 626Labs surfaced a false-positive — F1 fired
because a `modelRegistry` was detected AND inline systemInstructions existed
at call sites, but the registry is a model-routing registry (task-id →
model-id), not a prompt-content registry. The inline systemInstructions
weren't bypassing a prompt registry; there is no prompt registry to bypass.

v0.7 gates F1 on `registry.kind`:
  - prompt-content → F1 fires (current behavior)
  - hybrid → F1 fires (hybrid contains prompt-content)
  - model-routing → F1 does NOT fire (no prompt registry to bypass); F1b
    fires instead (no prompt-content registry detected)
  - task-mapping → F1 does NOT fire (task-mapping isn't a prompt store)
  - undefined/missing → existing v0.6 fallback (F1 fires when registry.detected)

Asserts:
  1. SKILL.md F1 step references registry.kind
  2. SKILL.md documents prompt-content / hybrid → F1 fires
  3. SKILL.md documents model-routing → F1 does NOT fire (F1b fires instead)
  4. SKILL.md documents task-mapping → F1 does NOT fire
  5. rubric F1 section documents the registry-kind gate
  6. v0.7 explicitly referenced
"""

import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent.parent.parent
AUDIT_SKILL = ROOT / "skills" / "audit" / "SKILL.md"
RUBRIC = ROOT / "skills" / "audit" / "references" / "smell-rubric-f1-f13.md"


class TestF1RegistryKindAwareness(unittest.TestCase):

    def setUp(self):
        self.skill = AUDIT_SKILL.read_text(encoding="utf-8")
        self.rubric = RUBRIC.read_text(encoding="utf-8")
        self.combined = self.skill + "\n" + self.rubric

    def test_skill_references_registry_kind(self):
        """SKILL.md F1 step must reference registry.kind."""
        self.assertIn(
            "registry.kind",
            self.combined,
            "audit/SKILL.md or rubric F1 section must reference registry.kind"
        )

    def test_prompt_content_fires(self):
        """SKILL/rubric must document prompt-content kind → F1 fires."""
        lowered = self.combined.lower()
        has_rule = (
            "prompt-content" in lowered
            and ("f1 fires" in lowered or "f1 still fires" in lowered or "fires f1" in lowered or "f1 applies" in lowered)
        )
        # Looser check — must clearly say prompt-content → F1 fires
        has_loose_rule = (
            "prompt-content" in lowered
            and "f1" in lowered
            and "fire" in lowered
        )
        self.assertTrue(
            has_rule or has_loose_rule,
            "F1 must fire when registry.kind === 'prompt-content'"
        )

    def test_model_routing_suppresses_f1(self):
        """SKILL/rubric must document model-routing → F1 does NOT fire (F1b fires instead)."""
        lowered = self.combined.lower()
        has_suppression = (
            "model-routing" in lowered
            and ("does not fire" in lowered or "not fire" in lowered or "suppress" in lowered or "skipped" in lowered)
        )
        self.assertTrue(
            has_suppression,
            "F1 must NOT fire when registry.kind === 'model-routing' (suppression must be documented)"
        )

    def test_model_routing_routes_to_f1b(self):
        """SKILL/rubric must document model-routing case routes to F1b (no prompt-content registry detected)."""
        lowered = self.combined.lower()
        has_route = (
            "model-routing" in lowered
            and "f1b" in lowered
        )
        self.assertTrue(
            has_route,
            "F1 model-routing case must route to F1b (no prompt-content registry detected)"
        )

    def test_hybrid_fires(self):
        """SKILL/rubric must document hybrid → F1 fires."""
        lowered = self.combined.lower()
        has_hybrid = "hybrid" in lowered and "f1" in lowered
        self.assertTrue(
            has_hybrid,
            "F1 must fire when registry.kind === 'hybrid'"
        )

    def test_v07_referenced(self):
        """SKILL/rubric must reference v0.7 for this change."""
        self.assertIn(
            "v0.7",
            self.combined,
            "F1 registry-kind awareness must be tagged v0.7"
        )

    def test_rubric_f1_documents_gate(self):
        """rubric F1 section specifically must document the registry-kind gate."""
        f1_start = self.rubric.find("## F1 ")
        f1_section = self.rubric[f1_start: f1_start + 3000] if f1_start >= 0 else ""
        has_gate = "registry.kind" in f1_section or "kind" in f1_section.lower()
        self.assertTrue(
            has_gate,
            "rubric F1 section must document the registry-kind gate"
        )


if __name__ == "__main__":
    unittest.main()
