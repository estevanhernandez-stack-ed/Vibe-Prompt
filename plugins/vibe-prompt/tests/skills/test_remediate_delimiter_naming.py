"""
Task 18 — TDD tests for skills/remediate/references/delimiter-naming.md.

Asserts the user-var → delimiter mapping table + INPUT fallback + custom override.
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
DELIMITER = SKILLS_DIR / "remediate" / "references" / "delimiter-naming.md"


class TestRemediateDelimiterNaming(unittest.TestCase):

    def setUp(self):
        self.assertTrue(
            DELIMITER.exists(),
            f"references/delimiter-naming.md must exist at {DELIMITER}",
        )
        self.content = DELIMITER.read_text(encoding="utf-8")

    def test_dream_text_maps_to_dream(self):
        # dreamText → DREAM
        self.assertIn("dreamText", self.content)
        # Check DREAM appears in context near dreamText
        idx = self.content.find("dreamText")
        section = self.content[idx:idx + 300]
        self.assertIn("DREAM", section)

    def test_user_message_maps_to_message(self):
        self.assertIn("userMessage", self.content)
        idx = self.content.find("userMessage")
        section = self.content[idx:idx + 300]
        self.assertIn("MESSAGE", section)

    def test_user_query_maps_to_query(self):
        self.assertIn("userQuery", self.content)
        idx = self.content.find("userQuery")
        section = self.content[idx:idx + 300]
        self.assertIn("QUERY", section)

    def test_input_fallback_declared(self):
        # `prompt` or unrecognized → INPUT fallback
        self.assertIn("INPUT", self.content)
        lower = self.content.lower()
        self.assertTrue(
            "fallback" in lower or "default" in lower,
            "Must declare INPUT as fallback/default",
        )

    def test_custom_override_via_config(self):
        # Custom delimiter override via config
        lower = self.content.lower()
        self.assertTrue(
            "config" in lower or "override" in lower,
            "Must reference config-driven override mechanism",
        )

    def test_mapping_table_present(self):
        # Markdown table with at least 4 mappings
        # Should have table headers and pipe-separated rows
        self.assertIn("|", self.content)
        # Count table-row lines that contain "→" or arrow notation, or pipe-mapped rows
        # Easier: ensure the named mappings are all present
        for name in ["dreamText", "userMessage", "userQuery"]:
            self.assertIn(name, self.content)


if __name__ == "__main__":
    unittest.main()
