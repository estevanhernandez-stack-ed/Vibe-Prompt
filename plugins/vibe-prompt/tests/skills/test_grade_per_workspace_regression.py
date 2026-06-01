"""
Task 32 (v0.7) — Per-workspace monotonic baseline regression in grade/SKILL.md.

Asserts that the monotonic baseline algorithm runs per-workspace, tracking regressions
separately from aggregate-level regression. flaggedRegressions entries gain an optional
workspaceIdentifier field (already in schema) and the SKILL.md workflow documents the
per-workspace baseline comparison.

Fixtures sketch:
  - Prior grade: appComposite.perWorkspace.cinema = 6.8
  - Current grade: appComposite.perWorkspace.cinema = 5.4
  - Expected: regression flagged on cinema workspace; flaggedRegressions[] entry carries
    workspaceIdentifier: "cinema"; aggregate-level regression tracked independently.
"""

import json
import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
GRADE_SKILL = SKILLS_DIR / "grade" / "SKILL.md"
MONOTONIC_REF = SKILLS_DIR / "grade" / "references" / "monotonic-baseline.md"
SCHEMAS_DIR = pathlib.Path(__file__).parent.parent.parent / "schemas"
GRADE_SCHEMA = SCHEMAS_DIR / "grade-result.schema.json"


class TestPerWorkspaceRegressionDocumented(unittest.TestCase):
    """SKILL.md documents per-workspace monotonic baseline tracking."""

    def setUp(self):
        self.grade = GRADE_SKILL.read_text(encoding="utf-8")
        self.monotonic = MONOTONIC_REF.read_text(encoding="utf-8")
        self.combined = self.grade + self.monotonic

    def test_grade_skill_documents_per_workspace_baseline(self):
        has_pw_baseline = "per-workspace baseline" in self.grade.lower()
        self.assertTrue(
            has_pw_baseline,
            "grade/SKILL.md must document per-workspace baseline comparison "
            "(literal phrase 'per-workspace baseline')",
        )

    def test_grade_skill_documents_per_workspace_regression(self):
        has_pw_regression = "per-workspace regression" in self.grade.lower()
        self.assertTrue(
            has_pw_regression,
            "grade/SKILL.md must document per-workspace regression tracking distinct "
            "from aggregate (literal phrase 'per-workspace regression')",
        )

    def test_grade_skill_documents_aggregate_separate_from_workspace(self):
        """Aggregate regression must be tracked separately from per-workspace regression."""
        has_separate = (
            "aggregate regression" in self.grade.lower()
            or "separately from aggregate" in self.grade.lower()
            or "aggregate-level regression" in self.grade.lower()
        )
        self.assertTrue(
            has_separate,
            "grade/SKILL.md must document aggregate regression as separate from per-workspace",
        )

    def test_grade_skill_documents_workspace_identifier_on_regression(self):
        """flaggedRegressions[].workspaceIdentifier must be populated per-workspace."""
        self.assertIn(
            "workspaceIdentifier",
            self.grade,
            "grade/SKILL.md must document populating flaggedRegressions[].workspaceIdentifier "
            "for per-workspace regressions",
        )


class TestRegressionSchemaShape(unittest.TestCase):
    """grade-result.schema.json exposes workspaceIdentifier on flaggedRegressions[]."""

    def setUp(self):
        self.schema = json.loads(GRADE_SCHEMA.read_text(encoding="utf-8"))

    def test_flagged_regressions_has_workspace_identifier(self):
        regressions = self.schema["properties"]["flaggedRegressions"]
        item = regressions["items"]
        self.assertIn(
            "workspaceIdentifier",
            item["properties"],
            "flaggedRegressions[].workspaceIdentifier must be schema-defined for v0.7",
        )

    def test_flagged_regression_workspace_identifier_nullable(self):
        """workspaceIdentifier must allow null for aggregate-level regression."""
        regressions = self.schema["properties"]["flaggedRegressions"]
        item = regressions["items"]
        ws_id = item["properties"]["workspaceIdentifier"]
        types = ws_id.get("type")
        if isinstance(types, list):
            self.assertIn(
                "null",
                types,
                "workspaceIdentifier on flaggedRegressions must allow null (aggregate-level)",
            )
        else:
            self.fail("workspaceIdentifier.type must permit null")


class TestPerWorkspaceMonotonicSemantics(unittest.TestCase):
    """SKILL.md preserves monotonic discipline at per-workspace granularity."""

    def setUp(self):
        self.grade = GRADE_SKILL.read_text(encoding="utf-8")

    def test_advance_baseline_per_workspace(self):
        """SKILL must document advancing baseline per workspace, not just aggregate."""
        text = self.grade.lower()
        has_advance = (
            "advance baseline per workspace" in text
            or "advance the baseline per workspace" in text
            or "advances baseline per workspace" in text
            or "advance per-workspace baseline" in text
        )
        self.assertTrue(
            has_advance,
            "grade/SKILL.md must document advancing baseline per-workspace explicitly",
        )

    def test_backcompat_single_workspace_baseline_path(self):
        """Single-workspace apps still run the v0.6 monotonic check unchanged."""
        has_backcompat = (
            "single-workspace" in self.grade.lower()
            or "back-compat" in self.grade.lower()
            or "backward" in self.grade.lower()
            or "v0.6 shape" in self.grade.lower()
            or "flat number" in self.grade.lower()
        )
        self.assertTrue(
            has_backcompat,
            "grade/SKILL.md must document single-workspace back-compat for monotonic baseline",
        )


if __name__ == "__main__":
    unittest.main()
