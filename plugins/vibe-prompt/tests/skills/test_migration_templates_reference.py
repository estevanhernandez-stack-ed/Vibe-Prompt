"""
Task 24 — TDD tests for skills/remediate/references/migration-templates.md.

Asserts the new v0.7 reference file exists and declares all three Category D
migration templates (D-1 inline-to-registry, D-2 typed-renderer, D-3
model-consolidation) with detection trigger, diff template, confidence default,
and routing default per task plan §24.
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
MIGRATION_TEMPLATES = (
    SKILLS_DIR / "remediate" / "references" / "migration-templates.md"
)


class TestMigrationTemplatesReference(unittest.TestCase):

    def setUp(self):
        self.assertTrue(
            MIGRATION_TEMPLATES.exists(),
            f"references/migration-templates.md must exist at {MIGRATION_TEMPLATES}",
        )
        self.content = MIGRATION_TEMPLATES.read_text(encoding="utf-8")
        self.lower = self.content.lower()

    # Section headers
    def test_has_d1_inline_to_registry_section(self):
        self.assertIn(
            "D-1 inline-to-registry",
            self.content,
            "reference must declare 'D-1 inline-to-registry' section",
        )

    def test_has_d2_typed_renderer_section(self):
        self.assertIn(
            "D-2 typed-renderer",
            self.content,
            "reference must declare 'D-2 typed-renderer' section",
        )

    def test_has_d3_model_consolidation_section(self):
        self.assertIn(
            "D-3 model-consolidation",
            self.content,
            "reference must declare 'D-3 model-consolidation' section",
        )

    # D-1 content
    def test_d1_documents_detection_trigger(self):
        idx = self.content.find("D-1 inline-to-registry")
        section = self.content[idx:idx + 4000]
        self.assertIn(
            "F1",
            section,
            "D-1 must reference F1 finding as the detection trigger",
        )
        # Inline systemInstruction is the trigger shape
        self.assertTrue(
            "inline" in section.lower() and ("systeminstruction" in section.lower() or "literal" in section.lower()),
            "D-1 must describe inline systemInstruction literal as trigger",
        )

    def test_d1_diff_template_includes_registry_entry_generation(self):
        idx = self.content.find("D-1 inline-to-registry")
        section = self.content[idx:idx + 4500]
        self.assertTrue(
            "registry" in section.lower() and "entry" in section.lower(),
            "D-1 template must describe registry entry generation",
        )

    def test_d1_diff_template_includes_call_site_replacement(self):
        idx = self.content.find("D-1 inline-to-registry")
        section = self.content[idx:idx + 4500]
        self.assertTrue(
            "getprompt" in section.lower() or "call site" in section.lower() or "call-site" in section.lower(),
            "D-1 template must describe call-site replacement (e.g., getPrompt(id))",
        )

    def test_d1_diff_template_includes_import_injection(self):
        idx = self.content.find("D-1 inline-to-registry")
        section = self.content[idx:idx + 4500]
        self.assertIn(
            "import",
            section.lower(),
            "D-1 template must reference import injection",
        )

    def test_d1_confidence_default_0_85(self):
        idx = self.content.find("D-1 inline-to-registry")
        section = self.content[idx:idx + 4500]
        self.assertIn("0.85", section, "D-1 default confidence is 0.85")

    def test_d1_routing_default_stage(self):
        idx = self.content.find("D-1 inline-to-registry")
        section = self.content[idx:idx + 4500]
        self.assertIn("stage", section.lower(), "D-1 routing default is stage")
        self.assertIn(
            "--apply-inline-to-registry",
            section,
            "D-1 must reference --apply-inline-to-registry opt-in flag",
        )

    # D-2 content
    def test_d2_documents_detection_trigger(self):
        idx = self.content.find("D-2 typed-renderer")
        section = self.content[idx:idx + 4000]
        self.assertIn(
            "F4",
            section,
            "D-2 must reference F4 finding as the detection trigger",
        )

    def test_d2_template_includes_required_vars(self):
        idx = self.content.find("D-2 typed-renderer")
        section = self.content[idx:idx + 4500]
        self.assertIn(
            "requiredVars",
            section,
            "D-2 template must include requiredVars interface addition",
        )

    def test_d2_template_includes_render_prompt_helper(self):
        idx = self.content.find("D-2 typed-renderer")
        section = self.content[idx:idx + 4500]
        self.assertIn(
            "renderPrompt",
            section,
            "D-2 template must include renderPrompt helper",
        )

    def test_d2_confidence_default_0_75(self):
        idx = self.content.find("D-2 typed-renderer")
        section = self.content[idx:idx + 4500]
        self.assertIn("0.75", section, "D-2 default confidence is 0.75")

    def test_d2_routing_default_stage(self):
        idx = self.content.find("D-2 typed-renderer")
        section = self.content[idx:idx + 4500]
        self.assertIn("stage", section.lower(), "D-2 routing default is stage")
        self.assertIn(
            "--apply-typed-renderer",
            section,
            "D-2 must reference --apply-typed-renderer opt-in flag",
        )

    # D-3 content
    def test_d3_documents_detection_trigger(self):
        idx = self.content.find("D-3 model-consolidation")
        section = self.content[idx:idx + 4000]
        self.assertIn(
            "F6",
            section,
            "D-3 must reference F6 finding as the detection trigger",
        )

    def test_d3_template_includes_config_path(self):
        idx = self.content.find("D-3 model-consolidation")
        section = self.content[idx:idx + 4500]
        self.assertTrue(
            "src/config/ai" in section or "config/ai.ts" in section,
            "D-3 template must reference src/config/ai.ts conventional path",
        )

    def test_d3_template_includes_default_model_export(self):
        idx = self.content.find("D-3 model-consolidation")
        section = self.content[idx:idx + 4500]
        self.assertIn(
            "DEFAULT_MODEL",
            section,
            "D-3 template must include DEFAULT_MODEL export",
        )

    def test_d3_confidence_default_0_88(self):
        idx = self.content.find("D-3 model-consolidation")
        section = self.content[idx:idx + 4500]
        self.assertIn("0.88", section, "D-3 default confidence is 0.88")

    def test_d3_routing_default_auto_write(self):
        idx = self.content.find("D-3 model-consolidation")
        section = self.content[idx:idx + 4500]
        self.assertTrue(
            "auto-write" in section.lower() or "auto write" in section.lower(),
            "D-3 routing default is auto-write at top end",
        )
        self.assertIn(
            "--apply-model-consolidation",
            section,
            "D-3 must reference --apply-model-consolidation opt-in flag",
        )

    def test_each_section_has_diff_template(self):
        # All three sections must show a concrete diff template
        for kind in ["D-1 inline-to-registry", "D-2 typed-renderer", "D-3 model-consolidation"]:
            idx = self.content.find(kind)
            section = self.content[idx:idx + 4500]
            self.assertTrue(
                "```" in section,
                f"{kind} must include a fenced code block (diff template)",
            )


if __name__ == "__main__":
    unittest.main()
