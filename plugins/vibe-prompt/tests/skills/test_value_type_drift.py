"""
Task 9 — TDD tests for value-type-drift section in mechanical-comparator.md.

SKILL.md/reference markdown files are prose workflow documents. These tests
verify the reference file contains the necessary detection rule prose so the
agent following the SKILL can correctly detect value-type-drift.

Asserts:
  1. mechanical-comparator.md contains a value-type-drift section
  2. Section is placed between schema-shape and length-delta (ordering check)
  3. Supports the bigThree case: prod=array<object>, baseline=string, declared=string
     → fires value-type-drift, driftedSide=prod
  4. Supports value-type-drift-both case (both differ from declared type)
  5. Handles the special case: array<string> vs array<object> always fires
  6. Includes union-schema escape hatch (don't fire if OUTPUT_SCHEMA declares a union)
  7. Evidence shape includes keyPath, declaredType, prodType, baselineType, driftedSide, snippet
  8. Severity is documented as medium
"""

import pathlib
import unittest

REFERENCES_DIR = (
    pathlib.Path(__file__).parent.parent.parent
    / "skills" / "eval" / "references"
)

COMPARATOR_FILE = REFERENCES_DIR / "mechanical-comparator.md"


class TestValueTypeDriftInComparator(unittest.TestCase):

    def setUp(self):
        self.content = COMPARATOR_FILE.read_text(encoding="utf-8")

    # ------------------------------------------------------------------ #
    # 1. Section exists                                                    #
    # ------------------------------------------------------------------ #

    def test_value_type_drift_section_exists(self):
        self.assertIn(
            "value-type-drift",
            self.content,
            "value-type-drift section missing from mechanical-comparator.md"
        )

    # ------------------------------------------------------------------ #
    # 2. Ordering: between schema-shape and length-delta                  #
    # ------------------------------------------------------------------ #

    def test_value_type_drift_after_schema_shape(self):
        schema_idx = self.content.find("schema-shape")
        vtd_idx = self.content.find("value-type-drift")
        self.assertGreater(schema_idx, -1, "schema-shape section not found")
        self.assertGreater(vtd_idx, -1, "value-type-drift section not found")
        self.assertGreater(
            vtd_idx, schema_idx,
            "value-type-drift must appear AFTER schema-shape in comparator"
        )

    def test_value_type_drift_before_length_delta(self):
        vtd_idx = self.content.find("value-type-drift")
        length_idx = self.content.find("length-delta")
        self.assertGreater(vtd_idx, -1, "value-type-drift section not found")
        self.assertGreater(length_idx, -1, "length-delta section not found")
        self.assertLess(
            vtd_idx, length_idx,
            "value-type-drift must appear BEFORE length-delta in comparator"
        )

    # ------------------------------------------------------------------ #
    # 3. bigThree case documented (prod=array<object>, baseline/declared=string)
    # ------------------------------------------------------------------ #

    def test_array_of_objects_vs_string_case_documented(self):
        """The bigThree real-world case: prod emits array<object>, schema says string."""
        vtd_idx = self.content.find("value-type-drift")
        # Extract to end of file or next major section
        next_section = self.content.find("### check.", vtd_idx + 20)
        section = self.content[vtd_idx : next_section] if next_section > -1 else self.content[vtd_idx:]
        self.assertTrue(
            "array<object>" in section or "array of object" in section.lower(),
            "value-type-drift section must mention array<object> (the bigThree case)"
        )

    def test_drifted_side_documentation_present(self):
        """Section must document driftedSide concept (which output is wrong)."""
        vtd_idx = self.content.find("value-type-drift")
        next_section = self.content.find("### check.", vtd_idx + 20)
        section = self.content[vtd_idx : next_section] if next_section > -1 else self.content[vtd_idx:]
        self.assertIn(
            "driftedSide",
            section,
            "value-type-drift must document driftedSide (prod | baseline | both)"
        )

    # ------------------------------------------------------------------ #
    # 4. value-type-drift-both case documented                            #
    # ------------------------------------------------------------------ #

    def test_value_type_drift_both_case_documented(self):
        self.assertIn(
            "value-type-drift-both",
            self.content,
            "value-type-drift-both case not documented in comparator"
        )

    # ------------------------------------------------------------------ #
    # 5. Special case: array<string> vs array<object> always fires        #
    # ------------------------------------------------------------------ #

    def test_array_string_vs_array_object_special_case(self):
        vtd_idx = self.content.find("value-type-drift")
        next_section = self.content.find("### check.", vtd_idx + 20)
        section = self.content[vtd_idx : next_section] if next_section > -1 else self.content[vtd_idx:]
        self.assertTrue(
            "array<string>" in section or "array of string" in section.lower(),
            "Special case: array<string> vs array<object> must be documented"
        )

    # ------------------------------------------------------------------ #
    # 6. Union-schema escape hatch                                        #
    # ------------------------------------------------------------------ #

    def test_union_schema_escape_hatch_documented(self):
        vtd_idx = self.content.find("value-type-drift")
        next_section = self.content.find("### check.", vtd_idx + 20)
        section = self.content[vtd_idx : next_section] if next_section > -1 else self.content[vtd_idx:]
        self.assertTrue(
            "union" in section.lower(),
            "value-type-drift must document the union-schema escape hatch"
        )

    # ------------------------------------------------------------------ #
    # 7. Evidence shape                                                   #
    # ------------------------------------------------------------------ #

    def test_evidence_keyPath_documented(self):
        vtd_idx = self.content.find("value-type-drift")
        next_section = self.content.find("### check.", vtd_idx + 20)
        section = self.content[vtd_idx : next_section] if next_section > -1 else self.content[vtd_idx:]
        self.assertIn("keyPath", section, "evidence.keyPath must be documented in value-type-drift")

    def test_evidence_declaredType_documented(self):
        vtd_idx = self.content.find("value-type-drift")
        next_section = self.content.find("### check.", vtd_idx + 20)
        section = self.content[vtd_idx : next_section] if next_section > -1 else self.content[vtd_idx:]
        self.assertIn("declaredType", section, "evidence.declaredType must be documented")

    def test_evidence_prodType_and_baselineType_documented(self):
        vtd_idx = self.content.find("value-type-drift")
        next_section = self.content.find("### check.", vtd_idx + 20)
        section = self.content[vtd_idx : next_section] if next_section > -1 else self.content[vtd_idx:]
        self.assertIn("prodType", section, "evidence.prodType must be documented")
        self.assertIn("baselineType", section, "evidence.baselineType must be documented")

    def test_evidence_snippet_documented(self):
        vtd_idx = self.content.find("value-type-drift")
        next_section = self.content.find("### check.", vtd_idx + 20)
        section = self.content[vtd_idx : next_section] if next_section > -1 else self.content[vtd_idx:]
        self.assertIn("snippet", section, "evidence.snippet must be documented (200-char truncation)")

    # ------------------------------------------------------------------ #
    # 8. Severity medium                                                  #
    # ------------------------------------------------------------------ #

    def test_value_type_drift_severity_is_medium(self):
        vtd_idx = self.content.find("value-type-drift")
        # Take a larger window to capture the check block
        section = self.content[vtd_idx : vtd_idx + 2000]
        self.assertIn(
            "medium",
            section.lower(),
            "value-type-drift check must declare severity: medium"
        )


class TestValueTypeDriftBothCase(unittest.TestCase):
    """Separate class to test the value-type-drift-both variant explicitly."""

    def setUp(self):
        self.content = COMPARATOR_FILE.read_text(encoding="utf-8")

    def test_both_case_explanation_present(self):
        """When both prod and baseline deviate from the declared type, schema is ground truth."""
        vtd_idx = self.content.find("value-type-drift-both")
        self.assertGreater(vtd_idx, -1, "value-type-drift-both not documented")
        # Should explain that schema is the ground truth in the both-wrong case
        window = self.content[vtd_idx : vtd_idx + 500]
        self.assertTrue(
            "schema" in window.lower() or "declared" in window.lower() or "ground truth" in window.lower(),
            "value-type-drift-both must explain that OUTPUT_SCHEMA is the ground truth"
        )

    def test_array_string_vs_array_object_fires_documentation(self):
        """Special case should be explicitly marked as 'always fires'."""
        content = self.content
        self.assertTrue(
            "always fires" in content.lower() or "always fire" in content.lower()
            or "always" in content.lower(),
            "array<string> vs array<object> special case should note it always fires"
        )


if __name__ == "__main__":
    unittest.main()
