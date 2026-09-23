"""
v0.8 — agent self-ID never defaults the model to a hardcoded id.

Pre-v0.8, agent-self-id.md defaulted Claude Code's model to
"claude-opus-4-7" and the eval / first-run-setup banners hardcoded it. A
stale evaluator id mislabels every judge footer, which is the exact thing
the evaluator-drift framing exists to get right.

Asserts:
  1. agent-self-id.md says detect-from-session-or-ask, never default
  2. No `default "<model-id>"` phrasing remains in the detection table
  3. eval + first-run-setup banners render agent.model, not a literal id
"""

import pathlib
import re
import unittest

SKILLS = pathlib.Path(__file__).parent.parent.parent / "skills"
SELF_ID = SKILLS / "first-run-setup" / "references" / "agent-self-id.md"
BANNERS = [SKILLS / "eval" / "SKILL.md", SKILLS / "first-run-setup" / "SKILL.md"]


class TestAgentSelfIdNoDefault(unittest.TestCase):

    def setUp(self):
        self.text = SELF_ID.read_text(encoding="utf-8")

    def test_detect_or_ask_rule(self):
        self.assertIn("detect from the session, or ask. Never default.", self.text)

    def test_no_default_model_phrasing(self):
        self.assertIsNone(
            re.search(r'[Dd]efault "(claude|gemini|gpt)-[^"]+"', self.text),
            "detection table must not default the model to a hardcoded id",
        )

    def test_unknown_fallback(self):
        self.assertIn('`model` field as `"unknown"`', self.text)

    def test_banners_render_agent_model(self):
        for path in BANNERS:
            text = path.read_text(encoding="utf-8")
            self.assertIn("({agent.model})", text, path.name)
            self.assertNotIn("claude-opus-4-7", text, path.name)


if __name__ == "__main__":
    unittest.main()
