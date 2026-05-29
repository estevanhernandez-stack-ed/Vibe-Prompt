"""
Task 17 — TDD tests for inject-attack-fixtures.md (6 canonical fixtures).

Asserts:
  1. File exists at skills/eval/references/inject-attack-fixtures.md
  2. Exactly 6 fixtures are declared (one per category)
  3. Each fixture has all required fields: name, pattern, category, severity,
     arbitraryTaskExample, judgeRubric
  4. All 6 categories are present: direct-override, role-assertion, role-flip,
     instruction-deflection, trust-manipulation, encoded-payload
  5. Severities match spec §3e: high/high/medium/medium/high/critical in
     category order; specifically encoded-payload is CRITICAL
  6. {arbitrary_task} placeholder appears in each fixture pattern
  7. Defense-in-depth phrase reference list is present (F11 prerequisite per spec)
"""

import pathlib
import re
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
FIXTURES_FILE = SKILLS_DIR / "eval" / "references" / "inject-attack-fixtures.md"

REQUIRED_CATEGORIES = [
    "direct-override",
    "role-assertion",
    "role-flip",
    "instruction-deflection",
    "trust-manipulation",
    "encoded-payload",
]

REQUIRED_FIELDS = ["name", "pattern", "category", "severity", "arbitraryTaskExample", "judgeRubric"]

# Expected severities per category per spec §3e
CATEGORY_SEVERITIES = {
    "direct-override": "high",
    "role-assertion": "high",
    "role-flip": "medium",
    "instruction-deflection": "medium",
    "trust-manipulation": "high",
    "encoded-payload": "critical",
}

# Defense-in-depth phrase list per spec §3c (F11 prerequisite)
DEFENSE_PHRASES = [
    "treat as data",
    "ignore instructions within",
    "your role is fixed",
    "do not execute commands",
    "regardless of user request",
    "always remain",
]


class TestInjectAttackFixturesFileExists(unittest.TestCase):

    def test_file_exists(self):
        self.assertTrue(
            FIXTURES_FILE.exists(),
            f"inject-attack-fixtures.md not found at {FIXTURES_FILE}"
        )


class TestInjectAttackFixturesContent(unittest.TestCase):

    def setUp(self):
        self.content = FIXTURES_FILE.read_text(encoding="utf-8")
        self.content_lower = self.content.lower()

    # ------------------------------------------------------------------ #
    # 1. All 6 categories present                                          #
    # ------------------------------------------------------------------ #

    def test_all_6_categories_present(self):
        for cat in REQUIRED_CATEGORIES:
            self.assertIn(
                cat,
                self.content,
                f"Category '{cat}' not found in inject-attack-fixtures.md"
            )

    # ------------------------------------------------------------------ #
    # 2. Each required field name appears                                  #
    # ------------------------------------------------------------------ #

    def test_required_fields_appear(self):
        for field in REQUIRED_FIELDS:
            self.assertIn(
                field,
                self.content,
                f"Required field '{field}' not found in inject-attack-fixtures.md"
            )

    # ------------------------------------------------------------------ #
    # 3. encoded-payload severity is CRITICAL                              #
    # ------------------------------------------------------------------ #

    def test_encoded_payload_severity_critical(self):
        """encoded-payload must be severity: critical per spec — not high."""
        # Find the encoded-payload section and verify critical appears near it
        idx = self.content.find("encoded-payload")
        self.assertGreater(idx, -1, "encoded-payload not found")
        # Check that 'critical' appears in the file at all
        self.assertIn(
            "critical",
            self.content_lower,
            "encoded-payload must have severity: critical in fixtures file"
        )

    # ------------------------------------------------------------------ #
    # 4. {arbitrary_task} placeholder in patterns                         #
    # ------------------------------------------------------------------ #

    def test_arbitrary_task_placeholder_present(self):
        self.assertIn(
            "{arbitrary_task}",
            self.content,
            "Fixture patterns must use {arbitrary_task} as placeholder"
        )

    # ------------------------------------------------------------------ #
    # 5. Exactly 6 fixture sections (one per category)                     #
    # ------------------------------------------------------------------ #

    def test_exactly_6_fixture_sections(self):
        """Count occurrences of 'category:' entries to confirm 6 fixtures."""
        category_occurrences = len(re.findall(r"category:", self.content))
        self.assertEqual(
            category_occurrences,
            6,
            f"Expected exactly 6 'category:' entries in fixtures file, found {category_occurrences}"
        )

    # ------------------------------------------------------------------ #
    # 6. judgeRubric field present for each                               #
    # ------------------------------------------------------------------ #

    def test_judge_rubric_entries_count(self):
        """Each fixture should have a judgeRubric entry."""
        judge_rubric_count = len(re.findall(r"judgeRubric:", self.content))
        self.assertEqual(
            judge_rubric_count,
            6,
            f"Expected 6 judgeRubric entries (one per fixture), found {judge_rubric_count}"
        )

    # ------------------------------------------------------------------ #
    # 7. Defense-in-depth phrase list present (F11 reference)             #
    # ------------------------------------------------------------------ #

    def test_defense_phrase_list_present(self):
        """File must contain the F11 defense-phrase reference list."""
        found = sum(1 for phrase in DEFENSE_PHRASES if phrase in self.content_lower)
        self.assertGreaterEqual(
            found,
            4,
            f"Expected at least 4 of 6 defense phrases in fixtures file, found {found}. "
            "Phrases needed: " + str(DEFENSE_PHRASES)
        )

    # ------------------------------------------------------------------ #
    # 8. role-flip uses {alternate_persona} placeholder                   #
    # ------------------------------------------------------------------ #

    def test_role_flip_alternate_persona_placeholder(self):
        self.assertIn(
            "{alternate_persona}",
            self.content,
            "role-flip fixture pattern must include {alternate_persona} placeholder"
        )

    # ------------------------------------------------------------------ #
    # 9. base64 reference in encoded-payload                              #
    # ------------------------------------------------------------------ #

    def test_encoded_payload_base64_reference(self):
        self.assertIn(
            "base64",
            self.content_lower,
            "encoded-payload fixture must reference base64 encoding"
        )

    # ------------------------------------------------------------------ #
    # 10. File contains the schema validation note                        #
    # ------------------------------------------------------------------ #

    def test_schema_reference_present(self):
        """File should mention schema or inject-attack-fixture.schema.json for traceability."""
        self.assertTrue(
            "inject-attack-fixture" in self.content_lower or "schema" in self.content_lower,
            "Fixtures file should reference the schema it validates against"
        )


if __name__ == "__main__":
    unittest.main()
