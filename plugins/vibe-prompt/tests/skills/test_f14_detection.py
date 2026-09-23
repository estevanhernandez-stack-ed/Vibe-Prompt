"""
v0.8 — contract tests for F14 (Model-migration API breakage).

F14 is agent-executed SKILL prose, so these tests pin the contract the prose
must carry: the four sub-case ids, the severity-by-model-resolution rule, the
critical false-positive guards (MCP callTool results, non-Anthropic responses,
OpenAI tool_choice), the suppression key, the cited sources, the remediation
path, and the explicit v0.9 out-of-scope note.

Asserts:
  1. Rubric carries an F14 section with severity, sub-cases, sources
  2. Severity rule: high for resolved 5.5-era / unresolved, medium older-pinned
  3. modelResolution values documented (resolved | unresolved | older-pinned)
  4. False-positive guards name the MCP and OpenAI real negatives
  5. Suppression via audit.f14.exceptions (file:line or prompt id)
  6. Recommendation points to the migration guide and /claude-api migrate
  7. Style advisories are declared out of scope (v0.9 candidates)
  8. audit/SKILL.md carries an F14 step with the same sub-cases and guards
  9. The rubric walk order in audit/SKILL.md ends in F14
"""

import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent.parent.parent
AUDIT_SKILL = ROOT / "skills" / "audit" / "SKILL.md"
RUBRIC = ROOT / "skills" / "audit" / "references" / "smell-rubric-f1-f13.md"

SUB_CASES = [
    "F14-thinking-param",
    "F14-forced-tool-choice",
    "F14-legacy-computer-tool",
    "F14-positional-content-read",
]

MIGRATION_GUIDE = "https://platform.claude.com/docs/en/models/opus-5-5/migration-guide"
WHATS_NEW = "https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5"


def _f14_section(text):
    start = text.find("## F14")
    if start < 0:
        return ""
    end = text.find("\n## ", start + 1)
    return text[start:end if end > 0 else len(text)]


def _skill_f14_step(text):
    start = text.find("4g. **F14")
    if start < 0:
        return ""
    end = text.find("\n5. ", start)
    return text[start:end if end > 0 else len(text)]


class TestF14Rubric(unittest.TestCase):

    def setUp(self):
        self.section = _f14_section(RUBRIC.read_text(encoding="utf-8"))

    def test_section_present(self):
        self.assertTrue(self.section, "rubric must carry a '## F14' section")
        self.assertIn("Model-migration API breakage", self.section)

    def test_all_sub_cases_documented(self):
        for sub in SUB_CASES:
            self.assertIn(sub, self.section, f"F14 section must document {sub}")

    def test_breaking_patterns_named(self):
        for token in [
            '"disabled"', "budget_tokens", '"any"', '"tool"',
            "computer_20251124", "computer_toolset_20260801",
            "content[0]", "thinking",
        ]:
            self.assertIn(token, self.section, f"F14 section must name {token}")

    def test_sources_cited(self):
        self.assertIn(MIGRATION_GUIDE, self.section)
        self.assertIn(WHATS_NEW, self.section)

    def test_target_model_ids_named(self):
        self.assertIn("claude-opus-5-5", self.section)
        self.assertIn("claude-fable-5-1", self.section)

    def test_severity_rule(self):
        lowered = self.section.lower()
        self.assertIn("high", lowered)
        self.assertIn("medium", lowered)
        self.assertIn("latent", lowered)

    def test_model_resolution_values(self):
        for value in ["resolved", "unresolved", "older-pinned"]:
            self.assertIn(f'"{value}"', self.section,
                          f"F14 must document modelResolution {value}")
        self.assertIn("modelResolution", self.section)

    def test_false_positive_guard_mcp(self):
        self.assertIn("callTool", self.section)
        self.assertIn("statusBar.ts:136", self.section)

    def test_false_positive_guard_openai_tool_choice(self):
        self.assertIn("openaiProvider.ts:79", self.section)
        self.assertIn("api.openai.com", self.section)

    def test_trace_must_end_at_anthropic_response(self):
        lowered = self.section.lower()
        self.assertIn("traces back to the messages response", lowered)

    def test_suppression_key(self):
        self.assertIn("audit.f14.exceptions", self.section)
        self.assertIn("file:line", self.section)

    def test_remediation_path(self):
        self.assertIn("/claude-api migrate", self.section)
        self.assertIn("no `:remediate` category", self.section)

    def test_style_advisories_out_of_scope(self):
        lowered = self.section.lower()
        self.assertIn("v0.9", lowered)
        self.assertIn("think carefully", lowered)
        self.assertIn("show your reasoning", lowered)

    def test_score_impact_declared(self):
        self.assertIn("instruction-clarity −1", self.section)
        self.assertIn("schema-tightness −1", self.section)

    def test_bedrock_computer_tool_exemption(self):
        self.assertIn("Bedrock", self.section)


class TestF14AuditSkill(unittest.TestCase):

    def setUp(self):
        self.skill = AUDIT_SKILL.read_text(encoding="utf-8")
        self.step = _skill_f14_step(self.skill)

    def test_step_present(self):
        self.assertTrue(self.step, "audit/SKILL.md must carry step 4g for F14")

    def test_step_sub_cases(self):
        for sub in SUB_CASES:
            self.assertIn(sub, self.step)

    def test_step_guards(self):
        self.assertIn("callTool", self.step)
        self.assertIn("statusBar.ts:136", self.step)
        self.assertIn("openaiProvider.ts:79", self.step)

    def test_step_exception_key(self):
        self.assertIn("audit.f14.exceptions", self.step)

    def test_step_sdk_markers(self):
        for marker in ["@anthropic-ai/sdk", "messages.create(", "api.anthropic.com/v1/messages"]:
            self.assertIn(marker, self.step)

    def test_step_finding_shape(self):
        self.assertIn('id: "F14"', self.step)
        self.assertIn("subCase", self.step)
        self.assertIn("modelResolution", self.step)

    def test_walk_order_ends_with_f14(self):
        self.assertIn("→ F13 → F14.", self.skill)

    def test_walk_order_includes_f6_subfindings(self):
        self.assertIn("F6 → F6-suspect-model → F6-retiring-model → F7", self.skill)

    def test_frontmatter_names_f1_f14(self):
        frontmatter = self.skill.split("---")[1]
        self.assertIn("F1-F14", frontmatter)


if __name__ == "__main__":
    unittest.main()
