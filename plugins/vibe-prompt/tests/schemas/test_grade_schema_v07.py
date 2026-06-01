"""
Task 6 (v0.7) — TDD tests for grade-result.schema.json v0.7 extensions.

Asserts:
  1. appComposite.perWorkspace optional object (keys = workspace names,
     values = composite numbers)
  2. appComposite.aggregate number (existing field semantics preserved)
  3. Backward compat: v0.6 grade-result.json (no perWorkspace key) validates;
     appComposite as flat number also still validates via oneOf
"""

import json
import pathlib
import unittest

from jsonschema import validate, ValidationError

SCHEMAS_DIR = pathlib.Path(__file__).parent.parent.parent / "schemas"
SCHEMA_PATH = SCHEMAS_DIR / "grade-result.schema.json"


def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def _minimal_grade(appComposite=8):
    return {
        "version": "0.3",
        "runId": "g-1",
        "computedAt": "2026-06-01T00:00:00Z",
        "perPrompt": {
            "natalReading": {
                "composite": 8,
                "dimensions": {
                    "schemaTightness": 8,
                    "personaConsistency": 9,
                    "instructionClarity": 8,
                    "tokenEfficiency": 7,
                },
            }
        },
        "appComposite": appComposite,
    }


def _appComposite_object_branch(schema):
    """Return the appComposite object-branch sub-schema (the second oneOf entry)."""
    ac = schema["properties"]["appComposite"]
    if "oneOf" in ac:
        for branch in ac["oneOf"]:
            if branch.get("type") == "object":
                return branch
    if ac.get("type") == "object":
        return ac
    raise AssertionError("Could not locate appComposite object branch")


class TestGradeV07AppCompositePerWorkspace(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_appComposite_object_branch_declares_perWorkspace(self):
        obj_branch = _appComposite_object_branch(self.schema)
        self.assertIn("perWorkspace", obj_branch["properties"])

    def test_appComposite_object_branch_declares_aggregate(self):
        obj_branch = _appComposite_object_branch(self.schema)
        self.assertIn("aggregate", obj_branch["properties"])

    def test_perWorkspace_is_open_object_keyed_by_workspace_name(self):
        obj_branch = _appComposite_object_branch(self.schema)
        pw = obj_branch["properties"]["perWorkspace"]
        self.assertEqual(pw["type"], "object")
        # additionalProperties (the workspace value) must accept null OR a number
        ap = pw["additionalProperties"]
        # accept either oneOf form or type: [number, null] form
        if "oneOf" in ap:
            types_seen = {b.get("type") for b in ap["oneOf"]}
            self.assertTrue("null" in types_seen or None in types_seen)
            self.assertTrue("number" in types_seen)
        else:
            t = ap.get("type")
            if isinstance(t, list):
                self.assertIn("number", t)
                self.assertIn("null", t)
            else:
                self.assertIn(t, ["number"])

    def test_workspacesWithNoFindings_array_declared(self):
        obj_branch = _appComposite_object_branch(self.schema)
        self.assertIn("workspacesWithNoFindings", obj_branch["properties"])
        wnf = obj_branch["properties"]["workspacesWithNoFindings"]
        self.assertEqual(wnf["type"], "array")
        self.assertEqual(wnf["items"]["type"], "string")

    def test_appComposite_object_form_accepts_perWorkspace(self):
        """The object form of appComposite must permit a perWorkspace map."""
        doc = _minimal_grade(
            appComposite={
                "value": 7,
                "aggregate": 7.1,
                "perWorkspace": {
                    "cinema": 6.5,
                    "hotel": 7.8,
                    "reel-battles": 7.0,
                },
            }
        )
        validate(instance=doc, schema=self.schema)


class TestGradeV07RegressionsWorkspaceIdentifier(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_flaggedRegressions_item_declares_workspaceIdentifier(self):
        item = self.schema["properties"]["flaggedRegressions"]["items"]
        self.assertIn("workspaceIdentifier", item["properties"])

    def test_flaggedRegressions_supports_workspaceIdentifier(self):
        doc = _minimal_grade()
        doc["flaggedRegressions"] = [
            {
                "promptId": "movie-trivia",
                "dimension": "personaConsistency",
                "delta": -2,
                "workspaceIdentifier": "cinema",
            }
        ]
        validate(instance=doc, schema=self.schema)


class TestGradeV07BackwardCompat(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_appComposite_as_flat_integer_still_validates(self):
        doc = _minimal_grade(appComposite=7)
        validate(instance=doc, schema=self.schema)

    def test_v06_grade_result_full_validates(self):
        doc = {
            "version": "0.3",
            "runId": "g-2026-05-29-abc",
            "computedAt": "2026-05-29T18:00:00Z",
            "sourceAuditRef": ".vibe-prompt/state/audit.json",
            "perPrompt": {
                "natalReading": {
                    "composite": 8,
                    "dimensions": {
                        "schemaTightness": 8,
                        "personaConsistency": 9,
                        "instructionClarity": 8,
                        "tokenEfficiency": 7,
                        "injectionResistance": 6,
                    },
                    "weights": {
                        "schemaTightness": 1.0,
                        "personaConsistency": 1.0,
                        "instructionClarity": 1.0,
                        "tokenEfficiency": 1.0,
                        "injectionResistance": 1.0,
                    },
                    "vsBaseline": {"delta": 0, "status": "stable"},
                }
            },
            "appComposite": {
                "value": 8,
                "dimensions": {
                    "schemaTightness": 8,
                    "personaConsistency": 9,
                    "instructionClarity": 8,
                    "tokenEfficiency": 7,
                    "injectionResistance": 6,
                },
            },
            "appCompositeVsBaseline": {"delta": 0, "status": "stable"},
            "flaggedRegressions": [],
        }
        validate(instance=doc, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
