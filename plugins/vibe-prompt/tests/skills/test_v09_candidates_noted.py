"""
v0.8 validation follow-up — known gaps are recorded as v0.9 candidates, not
silently shipped.

Asserts the rubric's F14 out-of-scope list and the 0.8.0 CHANGELOG entry both
name:
  1. date-stripping hiding fake dated ids (claude-haiku-4-20261022), with the
     dated-column check as the proposed fix
  2. the scan-scope gap for non-workspace root scripts/ dirs (QuizShow)
"""

import pathlib
import unittest

PLUGIN = pathlib.Path(__file__).parent.parent.parent
RUBRIC = PLUGIN / "skills" / "audit" / "references" / "smell-rubric-f1-f13.md"
CHANGELOG = PLUGIN.parent.parent / "CHANGELOG.md"


def _rubric_out_of_scope():
    text = RUBRIC.read_text(encoding="utf-8")
    start = text.find("**Out of scope for v0.8 (v0.9 candidates):**")
    return text[start:text.find("\n**Friction triggers:**", start)]


def _changelog_080():
    text = CHANGELOG.read_text(encoding="utf-8")
    start = text.find("## [0.8.0]")
    return text[start:text.find("\n## [0.7.1]", start)]


class TestV09CandidatesNoted(unittest.TestCase):

    def test_rubric_lists_both_gaps(self):
        section = _rubric_out_of_scope()
        self.assertIn("claude-haiku-4-20261022", section)
        self.assertIn("dated column", section)
        self.assertIn("root `scripts/`", section)
        self.assertIn("QuizShow", section)

    def test_changelog_lists_both_gaps(self):
        entry = _changelog_080()
        self.assertIn("### Known gaps (v0.9 candidates)", entry)
        self.assertIn("claude-haiku-4-20261022", entry)
        self.assertIn("root `scripts/`", entry)


if __name__ == "__main__":
    unittest.main()
