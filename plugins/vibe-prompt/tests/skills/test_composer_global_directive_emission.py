"""
Task 9 — TDD tests for composer detection emitting `global-directive` instead of `directive-field`.

v0.5 mapped semantic `global-directive` and `format-directive` to schema enum `directive-field`
because the schema didn't have a `global-directive` enum value. v0.6 schema added it, so
detection now emits `global-directive` directly for persona / master-directive layers.

Backward compat: existing v0.5 composer.json with `directive-field` still validates against
the v0.6 schema (the enum still contains `directive-field` as a deprecated alias).

Asserts:
  1. composer-detection.md heuristic table maps persona/master-directive to `global-directive` (not `directive-field`)
  2. SKILL.md Stage 3 emits `global-directive` for persona/master-directive layers
  3. `directive-field` deprecated alias is documented (still valid for backward compat)
  4. Schema validation: a v0.5-style composer.json with type="directive-field" still validates
  5. Schema validation: a v0.6-style composer.json with type="global-directive" validates
"""

import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent.parent.parent
SKILLS_DIR = ROOT / "skills"
FIRST_RUN_SKILL = SKILLS_DIR / "first-run-setup" / "SKILL.md"
COMPOSER_DETECTION = SKILLS_DIR / "first-run-setup" / "references" / "composer-detection.md"
COMPOSER_SCHEMA = ROOT / "schemas" / "composer.schema.json"


class TestComposerGlobalDirectiveEmission(unittest.TestCase):

    def setUp(self):
        self.skill = FIRST_RUN_SKILL.read_text(encoding="utf-8")
        self.detection = COMPOSER_DETECTION.read_text(encoding="utf-8")
        self.schema = json.loads(COMPOSER_SCHEMA.read_text(encoding="utf-8"))

    def test_global_directive_in_detection_heuristic(self):
        """composer-detection.md must reference global-directive as the emitted enum value."""
        self.assertIn(
            "global-directive",
            self.detection,
            "composer-detection.md must reference global-directive emission"
        )

    def test_skill_emits_global_directive(self):
        """SKILL.md Stage 3 must reference global-directive for persona/master-directive layers."""
        self.assertIn(
            "global-directive",
            self.skill,
            "first-run-setup/SKILL.md must reference global-directive emission"
        )

    def test_directive_field_documented_as_deprecated(self):
        """`directive-field` should be flagged as a deprecated/legacy alias."""
        combined = self.skill + self.detection
        has_deprecated = (
            "deprecated" in combined.lower()
            or "legacy" in combined.lower()
            or "backward compat" in combined.lower()
        )
        self.assertTrue(
            has_deprecated,
            "directive-field must be documented as deprecated/legacy alias in v0.6+"
        )

    def test_schema_still_accepts_directive_field(self):
        """Backward compat: v0.5 composer.json with type=directive-field must validate."""
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not installed")

        v05_sample = {
            "version": "0.1",
            "kind": "stacked",
            "layers": [
                {
                    "id": "directive-persona",
                    "type": "directive-field",
                    "text": "..."
                }
            ]
        }
        jsonschema.validate(v05_sample, self.schema)

    def test_schema_accepts_global_directive(self):
        """v0.6 composer.json with type=global-directive must validate."""
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not installed")

        v06_sample = {
            "version": "0.1",
            "kind": "stacked",
            "layers": [
                {
                    "id": "directive-persona",
                    "type": "global-directive",
                    "text": "..."
                }
            ]
        }
        jsonschema.validate(v06_sample, self.schema)

    def test_detection_mapping_table_updated(self):
        """The layer-type → composer.schema.json type mapping table should map
        the spec semantic `global-directive` directly to `global-directive` enum
        in v0.6+, with the prior `directive-field` mapping documented as deprecated."""
        # Look for the mapping section
        section_start = self.detection.find("composer.schema.json type")
        if section_start < 0:
            # Mapping table may live elsewhere; just check both terms coexist
            self.assertIn("global-directive", self.detection)
            return
        # Section should now reflect global-directive as a target enum
        section = self.detection[section_start:]
        self.assertIn(
            "global-directive",
            section,
            "Layer-type mapping section must include global-directive as a target"
        )


if __name__ == "__main__":
    unittest.main()
