"""
Task 31 (v0.7) — Per-workspace composite computation in grade/SKILL.md +
composite-formula.md.

Asserts that grade partitions findings by workspaceIdentifier and emits per-workspace
composites under appComposite.perWorkspace[<name>], with appComposite.aggregate as the
cross-workspace mean. Single-workspace apps (no workspaceIdentifier on findings) preserve
the v0.6 flat-number appComposite shape via the schema oneOf branch.

Fixtures sketch:
  - Fixture A: audit.json with findings tagged across 3 workspaces (cinema, hotel,
    reel-battles) → appComposite.perWorkspace has 3 keys, appComposite.aggregate is the
    cross-workspace mean.
  - Fixture B: workspace with zero findings → composite null + flagged in
    workspacesWithNoFindings[].
  - Fixture C: single-workspace audit (no workspaceIdentifier on any finding) → appComposite
    rendered as flat number (v0.6 shape) via oneOf branch.
"""

import json
import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
GRADE_SKILL = SKILLS_DIR / "grade" / "SKILL.md"
COMPOSITE_FORMULA = SKILLS_DIR / "grade" / "references" / "composite-formula.md"
SCHEMAS_DIR = pathlib.Path(__file__).parent.parent.parent / "schemas"
GRADE_SCHEMA = SCHEMAS_DIR / "grade-result.schema.json"


class TestGradePerWorkspaceDocumented(unittest.TestCase):
    """SKILL.md + composite-formula.md document per-workspace behavior."""

    def setUp(self):
        self.grade = GRADE_SKILL.read_text(encoding="utf-8")
        self.formula = COMPOSITE_FORMULA.read_text(encoding="utf-8")
        self.combined = self.grade + self.formula

    def test_grade_skill_references_workspace_identifier(self):
        self.assertIn(
            "workspaceIdentifier",
            self.grade,
            "grade/SKILL.md must reference workspaceIdentifier in the per-workspace partition step",
        )

    def test_grade_skill_documents_per_workspace_composites(self):
        self.assertIn(
            "perWorkspace",
            self.grade,
            "grade/SKILL.md must document emitting appComposite.perWorkspace per workspace",
        )

    def test_grade_skill_documents_aggregate_field(self):
        self.assertIn(
            "aggregate",
            self.grade,
            "grade/SKILL.md must document appComposite.aggregate as the cross-workspace mean",
        )

    def test_grade_skill_documents_workspaces_with_no_findings(self):
        self.assertIn(
            "workspacesWithNoFindings",
            self.grade,
            "grade/SKILL.md must document workspacesWithNoFindings[] for empty workspaces",
        )

    def test_composite_formula_documents_per_workspace(self):
        has_pw = (
            "perWorkspace" in self.formula
            or "per-workspace" in self.formula.lower()
            or "per workspace" in self.formula.lower()
        )
        self.assertTrue(
            has_pw,
            "composite-formula.md must document per-workspace composite computation",
        )

    def test_composite_formula_documents_aggregate_mean(self):
        has_aggregate = (
            "aggregate" in self.formula.lower()
            and ("mean" in self.formula.lower() or "average" in self.formula.lower())
        )
        self.assertTrue(
            has_aggregate,
            "composite-formula.md must document aggregate = cross-workspace mean",
        )

    def test_composite_formula_documents_v06_backcompat(self):
        """Single-workspace flat-number shape preserved (v0.6 oneOf branch)."""
        has_backcompat = (
            "single-workspace" in self.formula.lower()
            or "flat number" in self.formula.lower()
            or "v0.6" in self.formula
            or "back-compat" in self.formula.lower()
            or "backward" in self.formula.lower()
        )
        self.assertTrue(
            has_backcompat,
            "composite-formula.md must document v0.6 flat-number back-compat for single-workspace",
        )


class TestGradePerWorkspaceSchemaShape(unittest.TestCase):
    """Schema shape supports per-workspace + back-compat oneOf branches."""

    def setUp(self):
        self.schema = json.loads(GRADE_SCHEMA.read_text(encoding="utf-8"))

    def test_app_composite_oneof_has_perworkspace_branch(self):
        app_composite = self.schema["properties"]["appComposite"]
        self.assertIn("oneOf", app_composite)
        branches = app_composite["oneOf"]
        # Find the object-shape branch with perWorkspace
        object_branches = [b for b in branches if b.get("type") == "object"]
        self.assertTrue(object_branches, "appComposite oneOf must have an object-shape branch")
        obj = object_branches[0]
        self.assertIn("perWorkspace", obj["properties"])
        self.assertIn("aggregate", obj["properties"])

    def test_app_composite_oneof_preserves_flat_number(self):
        app_composite = self.schema["properties"]["appComposite"]
        branches = app_composite["oneOf"]
        # Flat-number branch (v0.6 back-compat)
        number_branches = [
            b for b in branches if b.get("type") in ("integer", "number")
        ]
        self.assertTrue(
            number_branches,
            "appComposite oneOf must preserve a flat-number branch for v0.6 single-workspace shape",
        )

    def test_workspaces_with_no_findings_field_present(self):
        app_composite = self.schema["properties"]["appComposite"]
        object_branches = [b for b in app_composite["oneOf"] if b.get("type") == "object"]
        obj = object_branches[0]
        self.assertIn(
            "workspacesWithNoFindings",
            obj["properties"],
            "object-shape appComposite must expose workspacesWithNoFindings[]",
        )

    def test_per_workspace_allows_null_composite(self):
        """Workspaces with zero findings get composite null."""
        app_composite = self.schema["properties"]["appComposite"]
        object_branches = [b for b in app_composite["oneOf"] if b.get("type") == "object"]
        pw = object_branches[0]["properties"]["perWorkspace"]
        addl = pw.get("additionalProperties", {})
        types = addl.get("type")
        if isinstance(types, list):
            self.assertIn(
                "null",
                types,
                "perWorkspace values must allow null (zero-findings workspace)",
            )
        else:
            self.fail("perWorkspace.additionalProperties.type must permit null")


class TestGradePerWorkspacePartitionLogic(unittest.TestCase):
    """Workflow describes partitioning audit findings by workspaceIdentifier."""

    def setUp(self):
        self.grade = GRADE_SKILL.read_text(encoding="utf-8")

    def test_partition_step_described(self):
        partition_words = ["partition", "group", "bucket", "split"]
        has_partition = any(w in self.grade.lower() for w in partition_words)
        self.assertTrue(
            has_partition,
            "grade/SKILL.md must describe partitioning findings by workspaceIdentifier",
        )

    def test_single_workspace_backcompat_path(self):
        has_backcompat = (
            "single-workspace" in self.grade.lower()
            or "no workspaceIdentifier" in self.grade
            or "v0.6 shape" in self.grade.lower()
            or "back-compat" in self.grade.lower()
            or "backward" in self.grade.lower()
            or "flat number" in self.grade.lower()
        )
        self.assertTrue(
            has_backcompat,
            "grade/SKILL.md must document the single-workspace v0.6 flat-number back-compat path",
        )


if __name__ == "__main__":
    unittest.main()
