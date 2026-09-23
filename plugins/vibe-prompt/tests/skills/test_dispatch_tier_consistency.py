"""
Regression test for GitHub issue #1: the guide's Model tiering section tagged
`:eval`'s LLM-judge dispatches `judgment` while eval/SKILL.md tags them
`instrument (calibrated)`, and vendor-clients.md still pinned the baseline call
to a bare `model: "haiku"`.

Asserts:
  1. guide and eval SKILL agree: the judge is `instrument (calibrated)`
  2. the guide no longer calls the judge `judgment`
  3. the judge reference files carry the same tier
  4. the InSessionAgentClient baseline carries a tier annotation, not a model
  5. no skill file pins a model via `model: "<name>"` (skills never name
     model IDs, per the family model-tiering RFC)
"""

import pathlib
import re
import unittest

SKILLS = pathlib.Path(__file__).parent.parent.parent / "skills"
GUIDE = SKILLS / "guide" / "SKILL.md"
EVAL = SKILLS / "eval" / "SKILL.md"
VENDOR_CLIENTS = SKILLS / "eval" / "references" / "vendor-clients.md"
JUDGE_REFS = [
    SKILLS / "eval" / "references" / "llm-judge-prompt.md",
    SKILLS / "eval" / "references" / "inject-attack-judge.md",
]

TIER = "instrument (calibrated)"


def _read(p):
    return p.read_text(encoding="utf-8")


def _section(text, heading):
    start = text.find(heading)
    end = text.find("\n## ", start + 1)
    return text[start:end if end > 0 else len(text)]


class TestJudgeTierAgreement(unittest.TestCase):

    def setUp(self):
        self.tiering = _section(_read(GUIDE), "## Model tiering")
        self.eval = _read(EVAL)

    def test_guide_judge_is_instrument(self):
        m = re.search(r"LLM-judge dispatches[^.]*?are `([^`]+)`", self.tiering)
        self.assertIsNotNone(m, "guide must state the judge dispatch tier")
        self.assertEqual(m.group(1), TIER)

    def test_guide_does_not_call_judge_judgment(self):
        self.assertNotRegex(self.tiering, r"LLM-judge dispatches[^.]*?are `judgment`")

    def test_eval_skill_judge_is_instrument(self):
        m = re.search(r"LLM-judge with Swap-and-Discard.*?\*\*Dispatch tier:\*\* `([^`]+)`",
                      self.eval, re.S)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), TIER)

    def test_judge_references_agree(self):
        for ref in JUDGE_REFS:
            self.assertIn(f"Dispatch tier: `{TIER}`", _read(ref), ref.name)


class TestBaselineTier(unittest.TestCase):

    def test_vendor_clients_baseline_has_tier(self):
        text = _read(VENDOR_CLIENTS)
        section = _section(text, "## InSessionAgentClient")
        self.assertIn(f"Dispatch tier: `{TIER}`", section)
        self.assertNotIn('model: "haiku"', section)

    def test_guide_names_baseline_tier(self):
        tiering = _section(_read(GUIDE), "## Model tiering")
        self.assertIn("baseline call is also `instrument (calibrated)`", tiering)


class TestNoModelPins(unittest.TestCase):

    def test_no_model_string_pins_in_skills(self):
        offenders = []
        for path in SKILLS.rglob("*.md"):
            for n, line in enumerate(_read(path).splitlines(), 1):
                if re.search(r'`model:\s*"[^"]+"`', line):
                    offenders.append(f"{path.relative_to(SKILLS)}:{n}")
        self.assertEqual(offenders, [], "skills never name model IDs; use a tier")


if __name__ == "__main__":
    unittest.main()
