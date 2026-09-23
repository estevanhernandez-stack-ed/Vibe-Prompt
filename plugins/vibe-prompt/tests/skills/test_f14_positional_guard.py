"""
v0.8 validation fix — F14-positional-content-read guard.

Real-app validation found the guard exempted "an explicit type check on the
same block", which is exactly the broken shape: when block 0 is `thinking`,
`content[0].type === 'text' ? content[0].text : ''` returns '' and
`const c = response.content[0]; if (c.type !== 'text') return []` skips the
result, both with no error.

Asserts (rubric §F14 and audit SKILL step 4g agree):
  1. The old exemption text is gone
  2. A type check on a fixed index is declared to fire, with both real shapes
  3. Only type-based selection across blocks (.find / .filter / loop) is exempt
  4. Positional shapes are generalized: [0], .at(0), destructuring, .shift(),
     1-indexed Lua content[1]
  5. The real positives from validation are cited in the rubric
"""

import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent.parent.parent
AUDIT_SKILL = ROOT / "skills" / "audit" / "SKILL.md"
RUBRIC = ROOT / "skills" / "audit" / "references" / "smell-rubric-f1-f13.md"

OLD_EXEMPTION = "or an explicit `type` check on the same block before reading `.text` does not fire"


def _rubric_f14():
    text = RUBRIC.read_text(encoding="utf-8")
    start = text.find("## F14")
    end = text.find("\n## ", start + 1)
    return text[start:end]


def _skill_4g():
    text = AUDIT_SKILL.read_text(encoding="utf-8")
    start = text.find("4g. **F14")
    end = text.find("\n5. ", start)
    return text[start:end]


class TestPositionalGuard(unittest.TestCase):

    def setUp(self):
        self.surfaces = {"rubric": _rubric_f14(), "skill": _skill_4g()}

    def test_old_exemption_removed(self):
        for name, text in self.surfaces.items():
            self.assertNotIn(OLD_EXEMPTION, text, name)
            self.assertNotIn("a `type` check on the same block) does not fire", text, name)

    def test_fixed_index_type_check_fires(self):
        for name, text in self.surfaces.items():
            self.assertIn("type check on a fixed index still fires", text.lower(), name)
            self.assertIn("content[0].type === 'text' ? content[0].text : ''", text, name)
            self.assertIn("if (c.type !== 'text') return []", text, name)

    def test_only_selection_exempt(self):
        for name, text in self.surfaces.items():
            self.assertIn("type-based selection across the blocks", text, name)
            self.assertIn(".find", text, name)
            self.assertIn(".filter", text, name)
            self.assertIn("loop", text, name)

    def test_positional_shapes_generalized(self):
        for name, text in self.surfaces.items():
            self.assertIn("reads the first block by position", text, name)
            for shape in [".at(0)", "const [first] = res.content", ".shift()", "content[1]"]:
                self.assertIn(shape, text, f"{name}: {shape}")
            self.assertIn("Lua", text, name)

    def test_real_positives_cited(self):
        rubric = self.surfaces["rubric"]
        for cite in [
            "functions/src/domains/ai/index.ts:76",
            "claude-question-gen.ts:287",
            ":363",
            ":443",
            "batch-personality-rewrite.ts:392",
        ]:
            self.assertIn(cite, rubric)


if __name__ == "__main__":
    unittest.main()
