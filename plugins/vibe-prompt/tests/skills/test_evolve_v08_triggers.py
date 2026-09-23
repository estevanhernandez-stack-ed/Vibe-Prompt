"""
v0.8 — friction triggers for F14 and F6-retiring-model, plus every surface
that enumerates the F-list.

Asserts:
  1. Each v0.8 trigger appears in friction-triggers.md with its confidence
  2. evolve-prompt/SKILL.md declares a v0.8 handler section covering each
  3. v0.7 triggers still present (no regression)
  4. F14 + F6-retiring-model reach every F-list surface: scoring table,
     report template, guide, fix-categories, README, plugin manifest
"""

import json
import pathlib
import re
import unittest

PLUGIN = pathlib.Path(__file__).parent.parent.parent
SKILLS_DIR = PLUGIN / "skills"
REPO = PLUGIN.parent.parent
FRICTION_TRIGGERS = SKILLS_DIR / "friction-logger" / "references" / "friction-triggers.md"
EVOLVE_SKILL = SKILLS_DIR / "evolve-prompt" / "SKILL.md"

V08_TRIGGERS = [
    ("f14-migration-breakage-detected", "medium"),
    ("f14-fired-on-non-anthropic-response", "low"),
    ("f6-retiring-model-detected", "medium"),
]


def _read(path):
    return path.read_text(encoding="utf-8")


class TestV08FrictionTriggers(unittest.TestCase):

    def setUp(self):
        self.catalog = _read(FRICTION_TRIGGERS)
        self.evolve = _read(EVOLVE_SKILL)

    def test_triggers_in_catalog_with_confidence(self):
        for code, conf in V08_TRIGGERS:
            pattern = rf"\|\s*`{re.escape(code)}`\s*\|\s*{conf}\s*\|"
            self.assertRegex(self.catalog, pattern, f"{code} ({conf}) missing from catalog")

    def test_catalog_v08_section(self):
        self.assertIn("## v0.8 triggers", self.catalog)

    def test_evolve_handlers(self):
        self.assertIn("**v0.8 trigger handler templates**", self.evolve)
        for code, _ in V08_TRIGGERS:
            self.assertIn(f"`{code}`", self.evolve)

    def test_v07_triggers_intact(self):
        for code in ["f6-suspect-model-detected", "composer-multiplicity-detected"]:
            self.assertIn(code, self.catalog)


class TestV08FindingSurfaces(unittest.TestCase):

    def test_scoring_table_rows(self):
        text = _read(SKILLS_DIR / "audit" / "references" / "scoring-dimensions.md")
        f14 = re.search(r"^\| \*\*F14\*\* \|.*$", text, re.M)
        self.assertIsNotNone(f14, "scoring table must carry an F14 row")
        cells = [c.strip().strip("*") for c in f14.group(0).strip("|").split("|")]
        # Finding | Severity | clarity | schema | persona | tokens | injection
        self.assertEqual(cells[2], "−1")
        self.assertEqual(cells[3], "−1")
        self.assertRegex(text, r"(?m)^\| \*\*F6-retiring-model\*\* \|")
        self.assertIn("**F14 rationale (v0.8):**", text)

    def test_report_template(self):
        text = _read(SKILLS_DIR / "audit" / "references" / "audit-report-template.md")
        self.assertIn("### F14 — Model-migration API breakage", text)
        self.assertIn("### F6-retiring-model", text)

    def test_guide_section(self):
        text = _read(SKILLS_DIR / "guide" / "SKILL.md")
        self.assertIn("## Opus 5.5 era readiness (v0.8)", text)
        self.assertIn("F14", text)
        self.assertIn("F6-retiring-model", text)

    def test_fix_categories_mapping(self):
        text = _read(SKILLS_DIR / "remediate" / "references" / "fix-categories.md")
        self.assertIn("F14 (model-migration API breakage, v0.8)", text)
        self.assertIn("F6-retiring-model", text)

    def test_readme_rubric_table(self):
        text = _read(REPO / "README.md")
        self.assertIn("F1–F14", text)
        self.assertRegex(text, r"(?m)^\| F14 \|")
        self.assertRegex(text, r"(?m)^\| F6-retiring-model \|")

    def test_manifest_description(self):
        manifest = json.loads(_read(PLUGIN / ".claude-plugin" / "plugin.json"))
        self.assertIn("F1-F14", manifest["description"])
        self.assertIn("F14", manifest["description"])

    def test_audit_command_description(self):
        text = _read(PLUGIN / "commands" / "audit.md")
        self.assertIn("F1-F14", text)


if __name__ == "__main__":
    unittest.main()
